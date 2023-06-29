from kubernetes import client, config
import sys
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


def format_output(configmap_names):
    if not configmap_names:
        return "No unused config maps found."

    table = Table(show_header=True, header_style="bold", title="Unused Config Maps")
    table.add_column("#", justify="right")
    table.add_column("Config Map Name")

    for i, name in enumerate(configmap_names, start=1):
        table.add_row(str(i), name)

    return table


def main(namespace):
    # Load the Kubernetes configuration
    config.load_kube_config()

    # Create Kubernetes API client
    api_instance = client.CoreV1Api()

    # Retrieve volumes and environment information
    volumesCM, volumesProjectedCM, envCM, envFromCM, envFromContainerCM = retrieve_volumes_and_env(api_instance,
                                                                                                   namespace)

    # Remove duplicates and sort the lists
    volumesCM = sorted(set(volumesCM))
    volumesProjectedCM = sorted(set(volumesProjectedCM))
    envCM = sorted(set(envCM))
    envFromCM = sorted(set(envFromCM))
    envFromContainerCM = sorted(set(envFromContainerCM))

    # Retrieve config map names
    configmap_names = retrieve_configmap_names(api_instance, namespace)

    # Calculate the difference between the two sets of names
    used_configmaps = volumesCM + volumesProjectedCM + envCM + envFromCM + envFromContainerCM
    diff = calculate_difference(used_configmaps, configmap_names)

    # Format and print the output
    output = format_output(diff)
    console = Console()
    console.print(output)


if __name__ == "__main__":
    # Check if the namespace is provided as a command-line argument
    if len(sys.argv) < 2:
        print("Please provide the namespace as a command-line argument.")
        sys.exit(1)

    # Retrieve the namespace from the command-line argument
    namespace = sys.argv[1]
    main(namespace)

