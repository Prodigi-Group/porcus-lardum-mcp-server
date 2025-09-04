param serverfarms_FLEX_porcus_lardum_mcp_bacb_name string = 'FLEX-porcus-lardum-mcp-bacb'

resource serverfarms_FLEX_porcus_lardum_mcp_bacb_name_resource 'Microsoft.Web/serverfarms@2024-11-01' = {
  name: serverfarms_FLEX_porcus_lardum_mcp_bacb_name
  location: 'North Europe'
  sku: {
    name: 'FC1'
    tier: 'FlexConsumption'
    size: 'FC1'
    family: 'FC'
    capacity: 0
  }
  kind: 'functionapp'
  properties: {
    perSiteScaling: false
    elasticScaleEnabled: false
    maximumElasticWorkerCount: 0
    isSpot: false
    reserved: true
    isXenon: false
    hyperV: false
    targetWorkerCount: 0
    targetWorkerSizeId: 0
    zoneRedundant: false
    asyncScalingEnabled: false
  }
}

output serverFarmId string = serverfarms_FLEX_porcus_lardum_mcp_bacb_name_resource.id
