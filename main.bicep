param location string = 'North Europe'
param appName string = 'porcus-lardum-mcp'
param storageAccountName string = 'porcuslardummcp'

module storageAccount 'storageaccount .bicep' = {
  name: 'storageAccount'
  params: {
    storageAccounts_porcuslardummcp_name: storageAccountName
  }
}

module flexConsumptionPlan 'flexconsumptionplan.bicep' = {
  name: 'flexConsumptionPlan'
  params: {
    serverfarms_FLEX_porcus_lardum_mcp_bacb_name: 'FLEX-${appName}-bacb'
  }
}

module applicationInsights 'appinisghts.bicep' = {
  name: 'applicationInsights'
  params: {
    components_porcuslardummcp_name: storageAccountName
    workspaces_DefaultWorkspace_northeurope_externalid: '/subscriptions/9d291a41-ab1a-47c4-9501-57c05937bef3/resourceGroups/DefaultResourceGroup-northeurope/providers/Microsoft.OperationalInsights/workspaces/DefaultWorkspace-northeurope'
  }
}

module functionApp 'functionapp.bicep' = {
  name: 'functionApp'
  params: {
    sites_porcus_lardum_mcp_name: appName
    serverfarms_FLEX_porcus_lardum_mcp_bacb_externalid: flexConsumptionPlan.outputs.serverFarmId
  }
  dependsOn: [
    storageAccount
    applicationInsights
    flexConsumptionPlan
  ]
}