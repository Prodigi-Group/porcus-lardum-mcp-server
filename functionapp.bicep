param sites_porcus_lardum_mcp_name string = 'porcus-lardum-mcp'
param serverfarms_FLEX_porcus_lardum_mcp_bacb_externalid string = '/subscriptions/9d291a41-ab1a-47c4-9501-57c05937bef3/resourceGroups/porcuslardummcp/providers/Microsoft.Web/serverfarms/FLEX-porcus-lardum-mcp-bacb'
param service_mcp_managment_externalid string = '/subscriptions/9d291a41-ab1a-47c4-9501-57c05937bef3/resourceGroups/rg-Prodigi-AI-MCP-Management/providers/Microsoft.ApiManagement/service/mcp-managment'

resource sites_porcus_lardum_mcp_name_resource 'Microsoft.Web/sites@2024-11-01' = {
  name: sites_porcus_lardum_mcp_name
  location: 'North Europe'
  tags: {
    'hidden-link: /app-insights-resource-id': '/subscriptions/9d291a41-ab1a-47c4-9501-57c05937bef3/resourceGroups/porcuslardummcp/providers/microsoft.insights/components/porcuslardummcp'
  }
  kind: 'functionapp,linux'
  properties: {
    enabled: true
    hostNameSslStates: [
      {
        name: '${sites_porcus_lardum_mcp_name}.azurewebsites.net'
        sslState: 'Disabled'
        hostType: 'Standard'
      }
      {
        name: '${sites_porcus_lardum_mcp_name}.scm.azurewebsites.net'
        sslState: 'Disabled'
        hostType: 'Repository'
      }
    ]
    serverFarmId: serverfarms_FLEX_porcus_lardum_mcp_bacb_externalid
    reserved: true
    isXenon: false
    hyperV: false
    dnsConfiguration: {}
    outboundVnetRouting: {
      allTraffic: false
      applicationTraffic: false
      contentShareTraffic: false
      imagePullTraffic: false
      backupRestoreTraffic: false
    }
    siteConfig: {
      numberOfWorkers: 1
      acrUseManagedIdentityCreds: false
      alwaysOn: false
      http20Enabled: false
      functionAppScaleLimit: 100
      minimumElasticInstanceCount: 0
    }
    functionAppConfig: {
      deployment: {
        storage: {
          type: 'blobcontainer'
          value: 'https://porcuslardummcp.blob.core.windows.net/app-package-${sites_porcus_lardum_mcp_name}-a0a6c90'
          authentication: {
            type: 'storageaccountconnectionstring'
            storageAccountConnectionStringName: 'DEPLOYMENT_STORAGE_CONNECTION_STRING'
          }
        }
      }
      runtime: {
        name: 'python'
        version: '3.13'
      }
      scaleAndConcurrency: {
        alwaysReady: []
        maximumInstanceCount: 100
        instanceMemoryMB: 512
        triggers: {}
      }
    }
    scmSiteAlsoStopped: false
    clientAffinityEnabled: false
    clientAffinityProxyEnabled: false
    clientCertEnabled: false
    clientCertMode: 'Required'
    hostNamesDisabled: false
    ipMode: 'IPv4'
    customDomainVerificationId: '8730C1C376CF400C1BCA71022FF2FC1A6545DA85C5738DEE1D8928C12007840A'
    containerSize: 1536
    dailyMemoryTimeQuota: 0
    httpsOnly: false
    endToEndEncryptionEnabled: false
    redundancyMode: 'None'
    publicNetworkAccess: 'Enabled'
    storageAccountRequired: false
    keyVaultReferenceIdentity: 'SystemAssigned'
  }
}

resource sites_porcus_lardum_mcp_name_ftp 'Microsoft.Web/sites/basicPublishingCredentialsPolicies@2024-11-01' = {
  parent: sites_porcus_lardum_mcp_name_resource
  name: 'ftp'
  location: 'North Europe'
  tags: {
    'hidden-link: /app-insights-resource-id': '/subscriptions/9d291a41-ab1a-47c4-9501-57c05937bef3/resourceGroups/porcuslardummcp/providers/microsoft.insights/components/porcuslardummcp'
  }
  properties: {
    allow: true
  }
}

resource sites_porcus_lardum_mcp_name_scm 'Microsoft.Web/sites/basicPublishingCredentialsPolicies@2024-11-01' = {
  parent: sites_porcus_lardum_mcp_name_resource
  name: 'scm'
  location: 'North Europe'
  tags: {
    'hidden-link: /app-insights-resource-id': '/subscriptions/9d291a41-ab1a-47c4-9501-57c05937bef3/resourceGroups/porcuslardummcp/providers/microsoft.insights/components/porcuslardummcp'
  }
  properties: {
    allow: true
  }
}

resource sites_porcus_lardum_mcp_name_web 'Microsoft.Web/sites/config@2024-11-01' = {
  parent: sites_porcus_lardum_mcp_name_resource
  name: 'web'
  location: 'North Europe'
  tags: {
    'hidden-link: /app-insights-resource-id': '/subscriptions/9d291a41-ab1a-47c4-9501-57c05937bef3/resourceGroups/porcuslardummcp/providers/microsoft.insights/components/porcuslardummcp'
  }
  properties: {
    numberOfWorkers: 1
    defaultDocuments: [
      'Default.htm'
      'Default.html'
      'Default.asp'
      'index.htm'
      'index.html'
      'iisstart.htm'
      'default.aspx'
      'index.php'
    ]
    netFrameworkVersion: 'v4.0'
    requestTracingEnabled: false
    remoteDebuggingEnabled: false
    httpLoggingEnabled: false
    acrUseManagedIdentityCreds: false
    logsDirectorySizeLimit: 35
    detailedErrorLoggingEnabled: false
    publishingUsername: '$porcus-lardum-mcp'
    scmType: 'None'
    use32BitWorkerProcess: false
    webSocketsEnabled: false
    alwaysOn: false
    managedPipelineMode: 'Integrated'
    virtualApplications: [
      {
        virtualPath: '/'
        physicalPath: 'site\\wwwroot'
        preloadEnabled: false
      }
    ]
    loadBalancing: 'LeastRequests'
    experiments: {
      rampUpRules: []
    }
    autoHealEnabled: false
    vnetRouteAllEnabled: false
    vnetPrivatePortsCount: 0
    apiManagementConfig: {
      id: '${service_mcp_managment_externalid}/apis/porcus-lardum-mcp'
    }
    localMySqlEnabled: false
    ipSecurityRestrictions: [
      {
        ipAddress: 'Any'
        action: 'Allow'
        priority: 2147483647
        name: 'Allow all'
        description: 'Allow all access'
      }
    ]
    scmIpSecurityRestrictions: [
      {
        ipAddress: 'Any'
        action: 'Allow'
        priority: 2147483647
        name: 'Allow all'
        description: 'Allow all access'
      }
    ]
    scmIpSecurityRestrictionsUseMain: false
    http20Enabled: false
    minTlsVersion: '1.2'
    scmMinTlsVersion: '1.2'
    ftpsState: 'FtpsOnly'
    preWarmedInstanceCount: 0
    functionAppScaleLimit: 100
    functionsRuntimeScaleMonitoringEnabled: false
    minimumElasticInstanceCount: 0
    azureStorageAccounts: {}
    http20ProxyFlag: 0
  }
}

resource sites_porcus_lardum_mcp_name_5fa2b711_ed3b_4f8d_89a5_8abc9cad25b5 'Microsoft.Web/sites/deployments@2024-11-01' = {
  parent: sites_porcus_lardum_mcp_name_resource
  name: '5fa2b711-ed3b-4f8d-89a5-8abc9cad25b5'
  location: 'North Europe'
  properties: {
    status: 4
    deployer: 'ms-azuretools-vscode'
    start_time: '2025-09-04T13:20:56.6766235Z'
    end_time: '2025-09-04T13:22:09.3833615Z'
    active: true
  }
}

resource sites_porcus_lardum_mcp_name_6ccaa720_27ea_4668_8a98_ebabf53a97ea 'Microsoft.Web/sites/deployments@2024-11-01' = {
  parent: sites_porcus_lardum_mcp_name_resource
  name: '6ccaa720-27ea-4668-8a98-ebabf53a97ea'
  location: 'North Europe'
  properties: {
    status: 4
    deployer: 'ms-azuretools-vscode'
    start_time: '2025-09-04T13:12:24.7237118Z'
    end_time: '2025-09-04T13:13:59.7008197Z'
    active: false
  }
}

resource sites_porcus_lardum_mcp_name_eec821b8_3086_4838_9ceb_dae2111b16fe 'Microsoft.Web/sites/deployments@2024-11-01' = {
  parent: sites_porcus_lardum_mcp_name_resource
  name: 'eec821b8-3086-4838-9ceb-dae2111b16fe'
  location: 'North Europe'
  properties: {
    status: 4
    deployer: 'ms-azuretools-vscode'
    start_time: '2025-09-04T13:18:44.3199422Z'
    end_time: '2025-09-04T13:19:57.010247Z'
    active: false
  }
}

resource sites_porcus_lardum_mcp_name_http_app_func 'Microsoft.Web/sites/functions@2024-11-01' = {
  parent: sites_porcus_lardum_mcp_name_resource
  name: 'http_app_func'
  location: 'North Europe'
  properties: {
    script_href: 'https://porcus-lardum-mcp.azurewebsites.net/admin/vfs/home/site/wwwroot/function_app.py'
    test_data_href: 'https://porcus-lardum-mcp.azurewebsites.net/admin/vfs/tmp/FunctionsData/http_app_func.dat'
    href: 'https://porcus-lardum-mcp.azurewebsites.net/admin/functions/http_app_func'
    config: {
      name: 'http_app_func'
      entryPoint: 'http_app_func'
      scriptFile: 'function_app.py'
      language: 'python'
      functionDirectory: '/home/site/wwwroot'
      bindings: [
        {
          direction: 'IN'
          type: 'httpTrigger'
          name: 'req'
          methods: [
            'GET'
            'POST'
            'DELETE'
            'HEAD'
            'PATCH'
            'PUT'
            'OPTIONS'
          ]
          authLevel: 'ANONYMOUS'
          route: '/{*route}'
        }
        {
          direction: 'OUT'
          type: 'http'
          name: '$return'
        }
      ]
    }
    invoke_url_template: 'https://porcus-lardum-mcp.azurewebsites.net//{*route}'
    language: 'python'
    isDisabled: false
  }
}

resource sites_porcus_lardum_mcp_name_sites_porcus_lardum_mcp_name_azurewebsites_net 'Microsoft.Web/sites/hostNameBindings@2024-11-01' = {
  parent: sites_porcus_lardum_mcp_name_resource
  name: '${sites_porcus_lardum_mcp_name}.azurewebsites.net'
  location: 'North Europe'
  properties: {
    siteName: 'porcus-lardum-mcp'
    hostNameType: 'Verified'
  }
}
