"""
Monitoring and metrics for crawler operations

This module provides:
- Performance metrics tracking
- Error rate monitoring
- Success/failure statistics
- Crawl job health checks
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import structlog
import asyncio
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = structlog.get_logger()


class CrawlMetrics:
    """
    In-memory metrics tracker for crawl operations

    Tracks:
    - Total crawls attempted
    - Success/failure rates
    - Validation error rates
    - Duplicate detection stats
    - Average crawl duration
    """

    def __init__(self):
        self.metrics = defaultdict(lambda: {
            'total': 0,
            'success': 0,
            'failed': 0,
            'validation_errors': 0,
            'duplicates': 0,
            'total_duration': 0.0,
            'last_run': None,
            'last_error': None
        })
        self.start_time = datetime.utcnow()

    def record_crawl(
        self,
        task_name: str,
        success: bool,
        duration: float,
        validation_errors: int = 0,
        duplicates: int = 0,
        error: Optional[str] = None
    ):
        """
        Record a crawl operation

        Args:
            task_name: Name of the crawl task
            success: Whether the crawl succeeded
            duration: Duration in seconds
            validation_errors: Number of validation errors
            duplicates: Number of duplicates detected
            error: Error message if failed
        """
        m = self.metrics[task_name]
        m['total'] += 1

        if success:
            m['success'] += 1
        else:
            m['failed'] += 1
            m['last_error'] = {
                'error': error,
                'timestamp': datetime.utcnow().isoformat()
            }

        m['validation_errors'] += validation_errors
        m['duplicates'] += duplicates
        m['total_duration'] += duration
        m['last_run'] = datetime.utcnow().isoformat()

        logger.info(
            "crawl_metrics_recorded",
            task=task_name,
            success=success,
            duration=duration,
            validation_errors=validation_errors,
            duplicates=duplicates
        )

    def get_metrics(self, task_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get metrics for a specific task or all tasks

        Args:
            task_name: Specific task name, or None for all

        Returns:
            Dictionary of metrics
        """
        if task_name:
            m = self.metrics.get(task_name, {})
            return self._calculate_rates(m)
        else:
            return {
                task: self._calculate_rates(m)
                for task, m in self.metrics.items()
            }

    def _calculate_rates(self, metrics: Dict) -> Dict[str, Any]:
        """Calculate derived metrics like success rate, avg duration"""
        total = metrics.get('total', 0)

        if total == 0:
            return {
                **metrics,
                'success_rate': 0.0,
                'failure_rate': 0.0,
                'avg_duration': 0.0,
                'validation_error_rate': 0.0,
                'duplicate_rate': 0.0
            }

        return {
            **metrics,
            'success_rate': round(metrics['success'] / total * 100, 2),
            'failure_rate': round(metrics['failed'] / total * 100, 2),
            'avg_duration': round(metrics['total_duration'] / total, 2),
            'validation_error_rate': round(metrics['validation_errors'] / total * 100, 2),
            'duplicate_rate': round(metrics['duplicates'] / total * 100, 2)
        }

    def get_health_status(self) -> Dict[str, Any]:
        """
        Get overall health status of crawler system

        Returns:
            Health status with recommendations
        """
        all_metrics = self.get_metrics()

        total_crawls = sum(m['total'] for m in all_metrics.values())
        total_failures = sum(m['failed'] for m in all_metrics.values())
        total_validation_errors = sum(m['validation_errors'] for m in all_metrics.values())

        # Calculate overall rates
        if total_crawls > 0:
            overall_failure_rate = total_failures / total_crawls * 100
            overall_validation_error_rate = total_validation_errors / total_crawls * 100
        else:
            overall_failure_rate = 0
            overall_validation_error_rate = 0

        # Determine health status
        if overall_failure_rate > 50:
            status = 'critical'
            message = 'High failure rate detected. Check crawler selectors and website structure.'
        elif overall_failure_rate > 20:
            status = 'warning'
            message = 'Moderate failure rate. Monitor for issues.'
        elif overall_validation_error_rate > 30:
            status = 'warning'
            message = 'High validation error rate. Check data quality.'
        else:
            status = 'healthy'
            message = 'All systems operating normally.'

        uptime = datetime.utcnow() - self.start_time

        return {
            'status': status,
            'message': message,
            'uptime_hours': round(uptime.total_seconds() / 3600, 2),
            'total_crawls': total_crawls,
            'overall_failure_rate': round(overall_failure_rate, 2),
            'overall_validation_error_rate': round(overall_validation_error_rate, 2),
            'task_metrics': all_metrics,
            'timestamp': datetime.utcnow().isoformat()
        }

    def reset_metrics(self, task_name: Optional[str] = None):
        """
        Reset metrics for a task or all tasks

        Args:
            task_name: Specific task to reset, or None for all
        """
        if task_name:
            if task_name in self.metrics:
                del self.metrics[task_name]
                logger.info("metrics_reset", task=task_name)
        else:
            self.metrics.clear()
            self.start_time = datetime.utcnow()
            logger.info("all_metrics_reset")


# Global metrics instance
crawl_metrics = CrawlMetrics()


class CrawlJobMonitor:
    """
    Monitor for crawl job execution and performance
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.jobs_collection = db.crawl_jobs

    async def log_job_start(
        self,
        task_name: str,
        task_id: str,
        params: Dict[str, Any]
    ) -> str:
        """
        Log the start of a crawl job

        Args:
            task_name: Name of the task
            task_id: Celery task ID
            params: Task parameters

        Returns:
            Job log ID
        """
        job_log = {
            'task_name': task_name,
            'task_id': task_id,
            'params': params,
            'status': 'running',
            'started_at': datetime.utcnow(),
            'completed_at': None,
            'duration': None,
            'result': None,
            'error': None
        }

        result = await self.jobs_collection.insert_one(job_log)

        logger.info(
            "crawl_job_started",
            job_id=str(result.inserted_id),
            task_name=task_name,
            task_id=task_id
        )

        return str(result.inserted_id)

    async def log_job_complete(
        self,
        task_id: str,
        result: Dict[str, Any],
        error: Optional[str] = None
    ):
        """
        Log the completion of a crawl job

        Args:
            task_id: Celery task ID
            result: Task result data
            error: Error message if failed
        """
        completed_at = datetime.utcnow()

        # Find the job log
        job_log = await self.jobs_collection.find_one({'task_id': task_id})

        if not job_log:
            logger.warning("job_log_not_found", task_id=task_id)
            return

        duration = (completed_at - job_log['started_at']).total_seconds()

        update_data = {
            'status': 'failed' if error else 'completed',
            'completed_at': completed_at,
            'duration': duration,
            'result': result,
            'error': error
        }

        await self.jobs_collection.update_one(
            {'task_id': task_id},
            {'$set': update_data}
        )

        # Record metrics
        crawl_metrics.record_crawl(
            task_name=job_log['task_name'],
            success=error is None,
            duration=duration,
            validation_errors=result.get('validation_errors', 0) + result.get('validation_failures', 0),
            duplicates=result.get('duplicates_skipped', 0),
            error=error
        )

        logger.info(
            "crawl_job_completed",
            job_id=str(job_log['_id']),
            task_name=job_log['task_name'],
            task_id=task_id,
            duration=duration,
            status=update_data['status']
        )

    async def get_recent_jobs(self, limit: int = 50) -> list:
        """
        Get recent crawl jobs

        Args:
            limit: Maximum number of jobs to return

        Returns:
            List of job logs
        """
        jobs = await self.jobs_collection.find().sort(
            'started_at', -1
        ).limit(limit).to_list(limit)

        return jobs

    async def get_job_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get statistics for crawl jobs in the last N hours

        Args:
            hours: Number of hours to look back

        Returns:
            Job statistics
        """
        since = datetime.utcnow() - timedelta(hours=hours)

        # Aggregate statistics
        pipeline = [
            {
                '$match': {
                    'started_at': {'$gte': since}
                }
            },
            {
                '$group': {
                    '_id': '$task_name',
                    'total_runs': {'$sum': 1},
                    'completed': {
                        '$sum': {'$cond': [{'$eq': ['$status', 'completed']}, 1, 0]}
                    },
                    'failed': {
                        '$sum': {'$cond': [{'$eq': ['$status', 'failed']}, 1, 0]}
                    },
                    'avg_duration': {'$avg': '$duration'},
                    'total_duration': {'$sum': '$duration'}
                }
            }
        ]

        stats = await self.jobs_collection.aggregate(pipeline).to_list(None)

        return {
            'period_hours': hours,
            'since': since.isoformat(),
            'task_stats': stats
        }


async def get_crawler_health() -> Dict[str, Any]:
    """
    Get comprehensive crawler health information

    Returns:
        Health status dictionary
    """
    health = crawl_metrics.get_health_status()

    logger.info("crawler_health_check", status=health['status'])

    return health


async def print_crawler_metrics():
    """
    Print crawler metrics to logs (for debugging)
    """
    metrics = crawl_metrics.get_metrics()
    health = await get_crawler_health()

    logger.info("=" * 60)
    logger.info("CRAWLER METRICS SUMMARY")
    logger.info("=" * 60)

    for task_name, task_metrics in metrics.items():
        logger.info(f"\n{task_name}:")
        logger.info(f"  Total Runs: {task_metrics['total']}")
        logger.info(f"  Success Rate: {task_metrics['success_rate']}%")
        logger.info(f"  Failure Rate: {task_metrics['failure_rate']}%")
        logger.info(f"  Avg Duration: {task_metrics['avg_duration']}s")
        logger.info(f"  Validation Errors: {task_metrics['validation_errors']}")
        logger.info(f"  Duplicates Found: {task_metrics['duplicates']}")
        logger.info(f"  Last Run: {task_metrics['last_run']}")

    logger.info(f"\nOVERALL HEALTH: {health['status'].upper()}")
    logger.info(f"Message: {health['message']}")
    logger.info(f"Uptime: {health['uptime_hours']} hours")
    logger.info("=" * 60)
