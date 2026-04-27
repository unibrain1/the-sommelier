---
name: sync
description: Trigger a full pipeline run on docker02 and stream the output
disable-model-invocation: true
---

Run the full pipeline on docker02:

```bash
ssh docker02 "cd /home/ansible/container/the-sommelier && docker compose run --rm run-now 2>&1"
```
