<template>
  <main class="flex min-h-screen items-center justify-center p-4 text-slate-100">
    <section class="w-full max-w-sm rounded-3xl border border-white/10 bg-slate-950/75 p-5 shadow-glow backdrop-blur-xl">
      <div class="mb-5 space-y-2">
        <p class="text-xs font-semibold uppercase tracking-[0.32em] text-cyan-300/80">Browser capture</p>
        <h1 class="text-2xl font-semibold tracking-tight text-white">Capture + Prompt</h1>
        <p class="text-sm leading-6 text-slate-300">
          Capture the active tab and include a prompt to generate an email draft.
        </p>
      </div>

      <label class="mb-4 block">
        <span class="mb-2 block text-xs font-semibold uppercase tracking-[0.22em] text-slate-300">Prompt</span>
        <textarea
          v-model="prompt"
          class="h-28 w-full resize-none rounded-2xl border border-white/10 bg-slate-900/70 px-3 py-2 text-sm text-slate-100 outline-none ring-cyan-300/50 transition focus:ring"
          placeholder="Example: Write a short outreach email based on this person's recent posts."
        ></textarea>
      </label>

      <button
        class="group relative flex w-full items-center justify-center overflow-hidden rounded-2xl bg-gradient-to-r from-cyan-400 via-sky-500 to-orange-400 px-4 py-3 text-sm font-semibold text-slate-950 transition duration-200 hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60"
        :disabled="busy"
        @click="sendPageHtml"
      >
        <span class="absolute inset-0 -translate-x-full bg-white/20 transition-transform duration-700 group-hover:translate-x-full"></span>
        <span class="relative">{{ busy ? 'Sending…' : 'Capture, send and draft' }}</span>
      </button>

      <p v-if="status" class="mt-4 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-200">
        {{ status }}
      </p>

      <p v-if="error" class="mt-3 rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">
        {{ error }}
      </p>

      <section
        v-if="generatedEmail"
        class="mt-3 rounded-2xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-100"
      >
        <p class="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-emerald-200">Generated email</p>
        <pre class="whitespace-pre-wrap font-sans leading-6">{{ generatedEmail }}</pre>
      </section>

      <p class="mt-4 text-xs leading-5 text-slate-400">
        API URL: <span class="text-slate-200">{{ apiUrl }}</span>
      </p>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';

type CapturedPage = {
  url: string;
  title: string;
  html: string;
};

type CaptureApiResponse = {
  id: number;
  source_url: string;
  page_title: string | null;
  html_file_path: string;
  created_at: string;
  email_response?: string | null;
};

const busy = ref(false);
const status = ref('');
const error = ref('');
const prompt = ref('');
const generatedEmail = ref('');
const apiUrl = computed(() => import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000/capture');

async function captureActiveTabHtml(): Promise<CapturedPage> {
  const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
  const tab = tabs[0];

  if (!tab?.id) {
    throw new Error('No active tab found.');
  }

  const [{ result }] = await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: () => ({
      url: window.location.href,
      title: document.title,
      html: document.documentElement.outerHTML,
    }),
  });

  if (!result) {
    throw new Error('Could not read the active page HTML.');
  }

  return result as CapturedPage;
}

async function sendPageHtml() {
  busy.value = true;
  status.value = '';
  error.value = '';
  generatedEmail.value = '';

  try {
    const page = await captureActiveTabHtml();

    const response = await fetch(apiUrl.value, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        source_url: page.url,
        page_title: page.title,
        html: page.html,
        prompt: prompt.value.trim() || null,
      }),
    });

    if (!response.ok) {
      throw new Error(`API request failed with status ${response.status}.`);
    }

    const payload = (await response.json()) as CaptureApiResponse;
    generatedEmail.value = payload.email_response?.trim() ?? '';
    status.value = generatedEmail.value
      ? `Sent ${page.title || page.url} and received an email draft.`
      : `Sent ${page.title || page.url} to the API.`;
  } catch (exception) {
    error.value = exception instanceof Error ? exception.message : 'An unknown error occurred.';
  } finally {
    busy.value = false;
  }
}
</script>