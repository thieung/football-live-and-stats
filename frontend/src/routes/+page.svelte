<script lang="ts">
	import { onMount } from 'svelte';
	import { matchesStore } from '$stores/matches';
	import { websocketStore } from '$stores/websocket';
	import MatchCard from '$components/MatchCard.svelte';
	import LoadingSpinner from '$components/LoadingSpinner.svelte';

	let liveMatches = [];
	let todayMatches = [];
	let loading = true;

	onMount(async () => {
		// Fetch live and today's matches
		await Promise.all([matchesStore.fetchLiveMatches(), matchesStore.fetchTodayMatches()]);

		loading = false;

		// Subscribe to live updates
		matchesStore.subscribe((matches) => {
			liveMatches = matches.live;
			todayMatches = matches.today;
		});

		// Subscribe to WebSocket for live updates
		websocketStore.subscribe('live:all');
	});
</script>

<svelte:head>
	<title>Live Football Scores - Football Live</title>
</svelte:head>

<div class="space-y-8">
	<!-- Live Matches Section -->
	<section>
		<div class="flex items-center justify-between mb-4">
			<h2 class="text-2xl font-bold flex items-center gap-2">
				<span class="inline-block w-3 h-3 bg-red-500 rounded-full animate-pulse-fast"></span>
				Live Matches
			</h2>
			<span class="text-sm text-gray-500">{liveMatches.length} matches</span>
		</div>

		{#if loading}
			<LoadingSpinner />
		{:else if liveMatches.length === 0}
			<div class="card text-center py-12 text-gray-500">
				<p class="text-lg">No live matches at the moment</p>
				<p class="text-sm mt-2">Check back soon for live updates!</p>
			</div>
		{:else}
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
				{#each liveMatches as match (match._id)}
					<MatchCard {match} />
				{/each}
			</div>
		{/if}
	</section>

	<!-- Today's Matches Section -->
	<section>
		<div class="flex items-center justify-between mb-4">
			<h2 class="text-2xl font-bold">Today's Matches</h2>
			<span class="text-sm text-gray-500">{todayMatches.length} matches</span>
		</div>

		{#if loading}
			<LoadingSpinner />
		{:else if todayMatches.length === 0}
			<div class="card text-center py-12 text-gray-500">
				<p class="text-lg">No matches scheduled for today</p>
			</div>
		{:else}
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
				{#each todayMatches as match (match._id)}
					<MatchCard {match} />
				{/each}
			</div>
		{/if}
	</section>
</div>
