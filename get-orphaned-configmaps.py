from kubernetes import client, config
import sys
import argparse
from rich.table import Table
from rich.console import Console


def retrieve_volumes_and_env(api_instance, namespace):
    volumesCM = []
    volumesProjectedCM = []
    envCM = []
    envFromCM = []
    envFromContainerCM = []

    # Retrieve pods in the specified namespace
    pods = api_instance.list_namespaced_pod(namespace)

    # Extract volume and environment information from pods
    for pod in pods.items:
        for volume in pod.spec.volumes:
            if volume.config_map:
                volumesCM.append(volume.config_map.name)
            if volume.projected:
                for source in volume.projected.sources:
                    if source.config_map:
                        volumesProjectedCM.append(source.config_map.name)
        for container in pod.spec.containers:
            if container.env:
                for env in container.env:
                    if env.value_from and env.value_from.config_map_key_ref:
                        envCM.append(env.value_from.config_map_key_ref.name)

            if container.env_from:
                for env_from in container.env_from:
                    if env_from.config_map_ref:
                        envFromCM.append(env_from.config_map_ref.name)
            if container.env_from:
                for env_from in container.env_from:
                    if env_from.config_map_ref:
                        envFromContainerCM.append(env_from.config_map_ref.name)

    return volumesCM, volumesProjectedCM, envCM, envFromCM, envFromContainerCM


def retrieve_configmap_names(api_instance, namespace):
    configmaps = api_instance.list_namespaced_config_map(namespace)
    return [configmap.metadata.name for configmap in configmaps.items]


def calculate_difference(used_configmaps, configmap_names):
    return sorted(set(configmap_names) - set(used_configmaps))


def format_output(namespace, configmap_names):
    if not configmap_names:
        return f"No unused config maps found in the namespace: {namespace}"

    table = Table(show_header=True, header_style="bold", title=f"Unused Config Maps in Namespace: {namespace}")
    table.add_column("#", justify="right")
    table.add_column("Config Map Name")

    for i, name in enumerate(configmap_names, start=1):
        table.add_row(str(i), name)

    return table


def process_namespace(api_instance, namespace):
    # Retrieve volumes and environment information for the namespace
    volumesCM, volumesProjectedCM, envCM, envFromCM, envFromContainerCM = retrieve_volumes_and_env(api_instance, namespace)

    # Remove duplicates and sort the lists
    volumesCM = sorted(set(volumesCM))
    volumesProjectedCM = sorted(set(volumesProjectedCM))
    envCM = sorted(set(envCM))
    envFromCM = sorted(set(envFromCM))
    envFromContainerCM = sorted(set(envFromContainerCM))

    # Retrieve config map names for the namespace
    configmap_names = retrieve_configmap_names(api_instance, namespace)

    # Calculate the difference between the two sets of names
    used_configmaps = volumesCM + volumesProjectedCM + envCM + envFromCM + envFromContainerCM
    diff = calculate_difference(used_configmaps, configmap_names)

    # Format and return the output for the namespace
    return format_output(namespace, diff)


def main(namespace):
    # Load the Kubernetes configuration
    config.load_kube_config()

    # Create Kubernetes API client
    api_instance = client.CoreV1Api()

    if namespace:
        # Process a specific namespace
        output = process_namespace(api_instance, namespace)
        console = Console()
        console.print(output)
    else:
        # Process all namespaces
        namespaces = api_instance.list_namespace()

        for ns in namespaces.items:
            namespace_name = ns.metadata.name
            output = process_namespace(api_instance, namespace_name)
            console = Console()
            console.print(output)
            console.print("\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Identify orphaned ConfigMaps in a Kubernetes namespace.")
    parser.add_argument("-n", "--namespace", help="Specify the namespace to scan for orphaned ConfigMaps.")
    args = parser.parse_args()

    main(args.namespace)
