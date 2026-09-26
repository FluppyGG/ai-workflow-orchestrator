# AI Workflow Orchestrator

Минимальный движок автоматизаций на Python.

## Идея

Описываем бизнес-процесс JSON-файлом, а движок выполняет шаги последовательно:

- `template` - формирование текста;
- `classify` - простая классификация;
- `llm` - запрос к OpenAI-compatible локальной/облачной модели;
- `http` - webhook/API;
- `delay` - задержка;
- `output` - сохранить итог.

Есть retry, таймауты, лог выполнения и dry-run.

## Пример

```bash
python run.py workflows/lead-triage.json examples/lead.json
```

## Для чего подходит

- AI-агенты;
- HR-воронки;
- обработка лидов;
- контент-конвейеры;
- Telegram/CRM интеграции;
- внутренние автоматизации.

## Конфигурация LLM

```bash
export LLM_BASE_URL=http://localhost:11434/v1
export LLM_API_KEY=ollama
export LLM_MODEL=qwen3:14b
export LLM_MOCK=true
```

## Что демонстрирует

- orchestration;
- retries;
- конфигурационный подход;
- интеграцию LLM;
- работу с API;
- сохранение трассировки выполнения.
