<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import { websocketStore } from '$stores/websocket';

	onMount(() => {
		// Connect to WebSocket on app mount
		websocketStore.connect();

		return () => {
			// Disconnect on unmount
			websocketStore.disconnect();
		};
	});
</script>

<div class="min-h-screen bg-gray-50">
	<!-- Header -->
	<header class="bg-white shadow">
		<nav class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="flex justify-between h-16">
				<div class="flex">
					<div class="flex-shrink-0 flex items-center">
						<a href="/" class="text-2xl font-bold text-primary-600">
							⚽ Football Live
						</a>
					</div>

					<div class="hidden sm:ml-6 sm:flex sm:space-x-8">
						<a
							href="/"
							class="border-primary-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
						>
							Live Scores
						</a>
						<a
							href="/leagues"
							class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
						>
							Leagues
						</a>
						<a
							href="/fixtures"
							class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
						>
							Fixtures
						</a>
					</div>
				</div>

				<div class="flex items-center">
					<a href="/auth/login" class="btn btn-primary"> Login </a>
				</div>
			</div>
		</nav>
	</header>

	<!-- Main Content -->
	<main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
		<slot />
	</main>

	<!-- Footer -->
	<footer class="bg-white border-t mt-12">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
			<p class="text-center text-gray-500 text-sm">
				© 2024 Football Live Score. All rights reserved.
			</p>
		</div>
	</footer>
</div>
