# Orphaned ConfigMaps

This repository contains a script to identify orphaned ConfigMaps in a Kubernetes namespace. Orphaned ConfigMaps are those that are not referenced by any active Pods or containers within the namespace.

## Prerequisites

Before running the script, make sure you have the following prerequisites installed:

- Python 3.x
- `pip` package installer

## Installation

1. Clone this repository to your local machine:

   ```shell
   git clone https://github.com/your-username/orphaned-configmaps.git
   ```
2. Change into the repository directory:
   ```shell
   cd orphaned-configmaps
   ```
3. Install the required Python dependencies:
   ```shell
   pip install -r requirements.txt
   ```

### Usage Examples

- To scan all namespaces for orphaned ConfigMaps:
    ```
    python orphaned_configmaps.py
    ```

- To specify one or more namespaces to scan for orphaned ConfigMaps:
    ```
    python orphaned_configmaps.py -n namespace1 namespace2
    ```

- To exclude specific namespaces from the scan:
    ```
    python orphaned_configmaps.py --exclude exclude_ns1 exclude_ns2
    ```

    Note: The `--exclude` flag cannot be used together with the `-n/--namespace` flag.


The script will display a table of orphaned ConfigMaps, if any are found.

## Example output
```shell

         Unused Config Maps in Namespace: my-namespace         
┏━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  # ┃ Config Map Name                                                 ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│  1 │ unused-configmap-1                                              │
│  2 │ super-important-configmap                                       │
└────┴─────────────────────────────────────────────────────────────────┘
  ```

## Caveat 
The script looks at pods and containers, so if you are consuming it in a deployment that is scaled to 0 it will not be detected. 
