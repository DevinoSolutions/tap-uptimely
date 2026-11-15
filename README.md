# tap-uptimely

Singer tap for [Uptimely](https://getuptimely.com), built with the [Meltano Singer SDK](https://sdk.meltano.com).

Reads the read-only `/v1` API ([docs](https://getuptimely.com/docs/api)). The free Uptimely plan includes
1,000 API requests a month, so a daily run of a small project fits.

## Streams

| Stream | Replication |
| --- | --- |
| `monitors` | full table |
| `monitor_status_history` | full table, child of `monitors` |
| `incidents` | incremental on `updated_at` |
| `alerts` | incremental on `updated_at` |
| `scheduled_maintenances` | full table |
| `status_pages` | full table |
| `status_page_resources` | full table, child of `status_pages` |

`incidents` and `alerts` are incremental. The API has no `updated_at` filter, so they still read every page
and only skip emitting unchanged rows. `monitors` and `status_pages` are full table because they are parents of
child streams and are small. Full-table streams emit an empty bookmark in the state, which is normal.

## Settings

| Setting | Required | Default |
| --- | --- | --- |
| `api_key` | yes | |
| `api_url` | no | `https://app.getuptimely.com` |
| `start_date` | no | |
| `page_size` | no | `100` |
| `status_history_days` | no | `30` |

Create the key in Uptimely under Settings, API Keys, Public API keys.

## Usage

```bash
pip install git+https://github.com/DevinoSolutions/tap-uptimely.git
TAP_UPTIMELY_API_KEY=... tap-uptimely --discover > catalog.json
TAP_UPTIMELY_API_KEY=... tap-uptimely --catalog catalog.json
```

With Meltano:

```bash
meltano add extractor tap-uptimely
meltano config tap-uptimely set api_key <key>
meltano run tap-uptimely target-jsonl
```

## Tests

```bash
pip install -e '.[dev]'
TAP_UPTIMELY_API_KEY=... pytest
```

The Singer SDK standard tests call the live API, so they use a few requests of your monthly quota and are
skipped when `TAP_UPTIMELY_API_KEY` is not set. `tests/test_offline.py` needs no key.

## License

Apache-2.0
