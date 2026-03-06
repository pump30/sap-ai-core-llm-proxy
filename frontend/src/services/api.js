export class ChatAPI {
  constructor(apiKey = '') {
    this.apiKey = apiKey;
  }

  setApiKey(apiKey) {
    this.apiKey = apiKey;
  }

  async getModels() {
    const res = await fetch('/v1/models', {
      headers: this.apiKey ? { 'Authorization': `Bearer ${this.apiKey}` } : {}
    });
    if (!res.ok) {
      throw new Error(`Failed to fetch models: ${res.status}`);
    }
    return res.json();
  }

  async *streamChat(messages, model, options = {}) {
    const res = await fetch('/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(this.apiKey ? { 'Authorization': `Bearer ${this.apiKey}` } : {})
      },
      body: JSON.stringify({
        model,
        messages,
        stream: true,
        ...options
      })
    });

    if (!res.ok) {
      const errorText = await res.text();
      throw new Error(`API Error: ${res.status} - ${errorText}`);
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();

      if (done) {
        break;
      }

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        const trimmedLine = line.trim();
        if (!trimmedLine || !trimmedLine.startsWith('data: ')) {
          continue;
        }

        const data = trimmedLine.slice(6);
        if (data === '[DONE]') {
          return;
        }

        try {
          const parsed = JSON.parse(data);
          const content = parsed.choices?.[0]?.delta?.content;
          if (content) {
            yield content;
          }
        } catch (e) {
          // Skip malformed JSON
        }
      }
    }
  }

  async chat(messages, model, options = {}) {
    const res = await fetch('/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(this.apiKey ? { 'Authorization': `Bearer ${this.apiKey}` } : {})
      },
      body: JSON.stringify({
        model,
        messages,
        stream: false,
        ...options
      })
    });

    if (!res.ok) {
      const errorText = await res.text();
      throw new Error(`API Error: ${res.status} - ${errorText}`);
    }

    return res.json();
  }

  async checkHealth() {
    const res = await fetch('/health');
    return res.ok;
  }

  async getOverview() {
    const res = await fetch('/api/overview', {
      headers: this.apiKey ? { 'Authorization': `Bearer ${this.apiKey}` } : {}
    });
    if (!res.ok) {
      throw new Error(`Failed to fetch overview: ${res.status}`);
    }
    return res.json();
  }
}

export const api = new ChatAPI();
