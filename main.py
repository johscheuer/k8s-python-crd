from kubernetes import client, config, watch

GROUP = 'stable.example.com'
RESOURCE_NAME = 'crontabs'

# https://github.com/kubernetes-client/python/issues/415
def create_crd(api_instance, crd):
    try:
        result = api_instance.create_custom_resource_definition(body=crd)
        print(result['code'])
        if result['code'] != 200:
            print(result['status'])
    except ValueError:
        pass

# Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()
v1 = client.CoreV1Api()

crd_metadata = client.V1ObjectMeta(name='%s.%s' % RESOURCE_NAME, GROUP)
crd_validation = client.V1beta1CustomResourceValidation(
    open_apiv3_schema=client.V1beta1JSONSchemaProps(
        properties={
            'cronSpec': client.V1beta1JSONSchemaProps(
                type='string',
                pattern='^(\d+|\*)(/\d+)?(\s+(\d+|\*)(/\d+)?){4}$',
            ),
            'replicas': client.V1beta1JSONSchemaProps(
                type='integer',
                minimum=1,
                maximum=10,
            )
        }
    )
)

crd_spec = client.V1beta1CustomResourceDefinitionSpec(
    group=GROUP,
    version='v1',
    scope='Namespaced',
    names=client.V1beta1CustomResourceDefinitionNames(
        plural=RESOURCE_NAME,
        singular='crontab',
        kind='CronTab',
        short_names=['ct']
    ),
    validation=crd_validation,
)

crd = client.V1beta1CustomResourceDefinition(
    api_version='apiextensions.k8s.io/v1beta1',
    kind='CustomResourceDefinition',
    metadata=crd_metadata,
    spec=crd_spec,
    status=None)

api_instance = client.ApiextensionsV1beta1Api()

result_list = api_instance.list_custom_resource_definition()
for item in result_list.items:
    if item.metadata.name == crd.metadata.name:
        print('CRD is already present')
        print(item.metadata.name)
    else:
        create_crd(api_instance, crd)

if len(result_list.items) == 0:
    create_crd(api_instance, crd)

# Watch all crds
crds = client.CustomObjectsApi()
resource_version = ''

for event in watch.Watch().stream(
        crds.list_cluster_custom_object,
        GROUP,
        'v1',
        RESOURCE_NAME,
        resource_version=resource_version):
    obj = event["object"]
    operation = event['type']
    spec = obj.get("spec")
    if not spec:
        continue
    metadata = obj.get("metadata")
    resource_version = metadata['resourceVersion']
    name = metadata['name']
    print("Handling %s on %s" % (operation, name))
