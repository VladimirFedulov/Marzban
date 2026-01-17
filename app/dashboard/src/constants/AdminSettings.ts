export type SettingInputType =
  | "boolean"
  | "number"
  | "text"
  | "textarea"
  | "select"
  | "custom";

export type SettingOption = {
  value: string;
  labelKey: string;
};

export type SettingDefinition = {
  key: string;
  labelKey: string;
  descriptionKey?: string;
  inputType: SettingInputType;
  options?: SettingOption[];
  delimiter?: string;
  requiresRestart?: boolean;
};

export type SettingsGroup = {
  id: string;
  titleKey: string;
  descriptionKey?: string;
  settings: SettingDefinition[];
};

export const settingsGroups: SettingsGroup[] = [
  {
    id: "status-texts",
    titleKey: "settings.groups.statusTexts",
    settings: [
      {
        key: "ACTIVE_STATUS_TEXT",
        labelKey: "settings.activeStatusText",
        descriptionKey: "settings.activeStatusTextHelp",
        inputType: "text",
      },
      {
        key: "EXPIRED_STATUS_TEXT",
        labelKey: "settings.expiredStatusText",
        descriptionKey: "settings.expiredStatusTextHelp",
        inputType: "text",
      },
      {
        key: "LIMITED_STATUS_TEXT",
        labelKey: "settings.limitedStatusText",
        descriptionKey: "settings.limitedStatusTextHelp",
        inputType: "text",
      },
      {
        key: "DISABLED_STATUS_TEXT",
        labelKey: "settings.disabledStatusText",
        descriptionKey: "settings.disabledStatusTextHelp",
        inputType: "text",
      },
      {
        key: "ONHOLD_STATUS_TEXT",
        labelKey: "settings.onHoldStatusText",
        descriptionKey: "settings.onHoldStatusTextHelp",
        inputType: "text",
      },
      {
        key: "USERS_AUTODELETE_DAYS",
        labelKey: "settings.usersAutodeleteDays",
        descriptionKey: "settings.usersAutodeleteDaysHelp",
        inputType: "number",
      },
      {
        key: "USER_AUTODELETE_INCLUDE_LIMITED_ACCOUNTS",
        labelKey: "settings.userAutodeleteIncludeLimitedAccounts",
        descriptionKey: "settings.userAutodeleteIncludeLimitedAccountsHelp",
        inputType: "boolean",
      },
    ],
  },
  {
    id: "subscription",
    titleKey: "settings.groups.subscription",
    settings: [
      {
        key: "SUB_UPDATE_INTERVAL",
        labelKey: "settings.subUpdateInterval",
        descriptionKey: "settings.subUpdateIntervalHelp",
        inputType: "text",
      },
      {
        key: "SUB_SUPPORT_URL",
        labelKey: "settings.subSupportUrl",
        descriptionKey: "settings.subSupportUrlHelp",
        inputType: "text",
      },
      {
        key: "SUB_PROFILE_TITLE",
        labelKey: "settings.subProfileTitle",
        descriptionKey: "settings.subProfileTitleHelp",
        inputType: "text",
      },
      {
        key: "SUBSCRIPTION_CUSTOM_HEADERS",
        labelKey: "settings.subscriptionCustomHeaders",
        descriptionKey: "settings.subscriptionCustomHeadersHelp",
        inputType: "custom",
      },
      {
        key: "SUBSCRIPTION_HIDE_DEFAULT_HOSTS_WHEN_CUSTOM_HOSTS",
        labelKey: "settings.subscriptionHideDefaultHosts",
        descriptionKey: "settings.subscriptionHideDefaultHostsHelp",
        inputType: "boolean",
      },
      {
        key: "SUBSCRIPTION_CUSTOM_NOTES_EXPIRED",
        labelKey: "settings.subscriptionCustomNotesExpired",
        descriptionKey: "settings.subscriptionCustomNotesExpiredHelp",
        inputType: "textarea",
        delimiter: "|",
      },
      {
        key: "SUBSCRIPTION_CUSTOM_NOTES_LIMITED",
        labelKey: "settings.subscriptionCustomNotesLimited",
        descriptionKey: "settings.subscriptionCustomNotesLimitedHelp",
        inputType: "textarea",
        delimiter: "|",
      },
      {
        key: "SUBSCRIPTION_CUSTOM_NOTES_DISABLED",
        labelKey: "settings.subscriptionCustomNotesDisabled",
        descriptionKey: "settings.subscriptionCustomNotesDisabledHelp",
        inputType: "textarea",
        delimiter: "|",
      },
      {
        key: "SUBSCRIPTION_CUSTOM_NOTES_HWID_LIMIT",
        labelKey: "settings.subscriptionCustomNotesHwidLimit",
        descriptionKey: "settings.subscriptionCustomNotesHwidLimitHelp",
        inputType: "textarea",
        delimiter: "|",
      },
    ],
  },
  {
    id: "hwid",
    titleKey: "settings.groups.hwid",
    settings: [
      {
        key: "HWID_DEVICE_LIMIT_ENABLED",
        labelKey: "settings.hwidDeviceLimitEnabled",
        descriptionKey: "settings.hwidDeviceLimitEnabledHelp",
        inputType: "select",
        options: [
          {
            value: "enabled",
            labelKey: "settings.hwidLimitEnabled",
          },
          {
            value: "disabled",
            labelKey: "settings.hwidLimitDisabled",
          },
          {
            value: "logging",
            labelKey: "settings.hwidLimitLogging",
          },
        ],
      },
      {
        key: "HWID_FALLBACK_DEVICE_LIMIT",
        labelKey: "settings.hwidFallbackDeviceLimit",
        descriptionKey: "settings.hwidFallbackDeviceLimitHelp",
        inputType: "number",
      },
      {
        key: "HWID_DEVICE_RETENTION_DAYS",
        labelKey: "settings.hwidDeviceRetentionDays",
        descriptionKey: "settings.hwidDeviceRetentionDaysHelp",
        inputType: "number",
      },
    ],
  },
  {
    id: "templates",
    titleKey: "settings.groups.templates",
    descriptionKey: "settings.groups.templatesDescription",
    settings: [
      {
        key: "CUSTOM_TEMPLATES_DIRECTORY",
        labelKey: "settings.customTemplatesDirectory",
        descriptionKey: "settings.customTemplatesDirectoryHelp",
        inputType: "text",
      },
      {
        key: "SUBSCRIPTION_PAGE_TEMPLATE",
        labelKey: "settings.subscriptionPageTemplate",
        descriptionKey: "settings.subscriptionPageTemplateHelp",
        inputType: "text",
      },
      {
        key: "HOME_PAGE_TEMPLATE",
        labelKey: "settings.homePageTemplate",
        descriptionKey: "settings.homePageTemplateHelp",
        inputType: "text",
      },
      {
        key: "CLASH_SUBSCRIPTION_TEMPLATE",
        labelKey: "settings.clashSubscriptionTemplate",
        descriptionKey: "settings.clashSubscriptionTemplateHelp",
        inputType: "text",
      },
      {
        key: "CLASH_SETTINGS_TEMPLATE",
        labelKey: "settings.clashSettingsTemplate",
        descriptionKey: "settings.clashSettingsTemplateHelp",
        inputType: "text",
      },
      {
        key: "SINGBOX_SUBSCRIPTION_TEMPLATE",
        labelKey: "settings.singboxSubscriptionTemplate",
        descriptionKey: "settings.singboxSubscriptionTemplateHelp",
        inputType: "text",
      },
      {
        key: "SINGBOX_SETTINGS_TEMPLATE",
        labelKey: "settings.singboxSettingsTemplate",
        descriptionKey: "settings.singboxSettingsTemplateHelp",
        inputType: "text",
      },
      {
        key: "MUX_TEMPLATE",
        labelKey: "settings.muxTemplate",
        descriptionKey: "settings.muxTemplateHelp",
        inputType: "text",
      },
      {
        key: "V2RAY_SUBSCRIPTION_TEMPLATE",
        labelKey: "settings.v2raySubscriptionTemplate",
        descriptionKey: "settings.v2raySubscriptionTemplateHelp",
        inputType: "text",
      },
      {
        key: "V2RAY_SETTINGS_TEMPLATE",
        labelKey: "settings.v2raySettingsTemplate",
        descriptionKey: "settings.v2raySettingsTemplateHelp",
        inputType: "text",
      },
      {
        key: "V2RAY_TEMPLATE_MAPPING",
        labelKey: "settings.v2rayTemplateMapping",
        descriptionKey: "settings.v2rayTemplateMappingHelp",
        inputType: "text",
      },
      {
        key: "EXTERNAL_CONFIG",
        labelKey: "settings.externalConfig",
        descriptionKey: "settings.externalConfigHelp",
        inputType: "text",
      },
    ],
  },
  {
    id: "subscription-advanced",
    titleKey: "settings.groups.subscriptionAdvanced",
    settings: [
      {
        key: "XRAY_SUBSCRIPTION_URL_PREFIX",
        labelKey: "settings.xraySubscriptionUrlPrefix",
        descriptionKey: "settings.xraySubscriptionUrlPrefixHelp",
        inputType: "text",
      },
      {
        key: "XRAY_SUBSCRIPTION_PATH",
        labelKey: "settings.xraySubscriptionPath",
        descriptionKey: "settings.xraySubscriptionPathHelp",
        inputType: "text",
      },
    ],
  },
  {
    id: "client-json",
    titleKey: "settings.groups.clientJson",
    descriptionKey: "settings.groups.clientJsonDescription",
    settings: [
      {
        key: "USE_CUSTOM_JSON_DEFAULT",
        labelKey: "settings.useCustomJsonDefault",
        descriptionKey: "settings.useCustomJsonDefaultHelp",
        inputType: "boolean",
      },
      {
        key: "USE_CUSTOM_JSON_FOR_V2RAYN",
        labelKey: "settings.useCustomJsonForV2rayn",
        descriptionKey: "settings.useCustomJsonForV2raynHelp",
        inputType: "boolean",
      },
      {
        key: "USE_CUSTOM_JSON_FOR_V2RAYNG",
        labelKey: "settings.useCustomJsonForV2rayng",
        descriptionKey: "settings.useCustomJsonForV2rayngHelp",
        inputType: "boolean",
      },
      {
        key: "USE_CUSTOM_JSON_FOR_STREISAND",
        labelKey: "settings.useCustomJsonForStreisand",
        descriptionKey: "settings.useCustomJsonForStreisandHelp",
        inputType: "boolean",
      },
      {
        key: "USE_CUSTOM_JSON_FOR_HAPP",
        labelKey: "settings.useCustomJsonForHapp",
        descriptionKey: "settings.useCustomJsonForHappHelp",
        inputType: "boolean",
      },
      {
        key: "USE_CUSTOM_JSON_FOR_NPVTUNNEL",
        labelKey: "settings.useCustomJsonForNpvtunnel",
        descriptionKey: "settings.useCustomJsonForNpvtunnelHelp",
        inputType: "boolean",
      },
    ],
  },
  {
    id: "jobs",
    titleKey: "settings.groups.jobs",
    settings: [
      {
        key: "JOB_CORE_HEALTH_CHECK_INTERVAL",
        labelKey: "settings.jobCoreHealthCheckInterval",
        descriptionKey: "settings.jobCoreHealthCheckIntervalHelp",
        inputType: "number",
        requiresRestart: true,
      },
      {
        key: "JOB_RECORD_NODE_USAGES_INTERVAL",
        labelKey: "settings.jobRecordNodeUsagesInterval",
        descriptionKey: "settings.jobRecordNodeUsagesIntervalHelp",
        inputType: "number",
        requiresRestart: true,
      },
      {
        key: "JOB_RECORD_USER_USAGES_INTERVAL",
        labelKey: "settings.jobRecordUserUsagesInterval",
        descriptionKey: "settings.jobRecordUserUsagesIntervalHelp",
        inputType: "number",
        requiresRestart: true,
      },
      {
        key: "JOB_REVIEW_USERS_INTERVAL",
        labelKey: "settings.jobReviewUsersInterval",
        descriptionKey: "settings.jobReviewUsersIntervalHelp",
        inputType: "number",
        requiresRestart: true,
      },
      {
        key: "JOB_SEND_NOTIFICATIONS_INTERVAL",
        labelKey: "settings.jobSendNotificationsInterval",
        descriptionKey: "settings.jobSendNotificationsIntervalHelp",
        inputType: "number",
        requiresRestart: true,
      },
      {
        key: "JOB_RECORD_REALTIME_BANDWIDTH_INTERVAL",
        labelKey: "settings.jobRecordRealtimeBandwidthInterval",
        descriptionKey: "settings.jobRecordRealtimeBandwidthIntervalHelp",
        inputType: "number",
        requiresRestart: true,
      },
      {
        key: "JOB_RECORD_USER_USAGES_WORKERS",
        labelKey: "settings.jobRecordUserUsagesWorkers",
        descriptionKey: "settings.jobRecordUserUsagesWorkersHelp",
        inputType: "number",
        requiresRestart: true,
      },
      {
        key: "JOB_CORE_HEALTH_CHECK_MAX_INSTANCES",
        labelKey: "settings.jobCoreHealthCheckMaxInstances",
        descriptionKey: "settings.jobCoreHealthCheckMaxInstancesHelp",
        inputType: "number",
        requiresRestart: true,
      },
      {
        key: "JOB_RECORD_USER_USAGES_MAX_INSTANCES",
        labelKey: "settings.jobRecordUserUsagesMaxInstances",
        descriptionKey: "settings.jobRecordUserUsagesMaxInstancesHelp",
        inputType: "number",
        requiresRestart: true,
      },
      {
        key: "JOB_RECORD_NODE_USAGES_MAX_INSTANCES",
        labelKey: "settings.jobRecordNodeUsagesMaxInstances",
        descriptionKey: "settings.jobRecordNodeUsagesMaxInstancesHelp",
        inputType: "number",
        requiresRestart: true,
      },
      {
        key: "JOB_RECORD_REALTIME_BANDWIDTH_MAX_INSTANCES",
        labelKey: "settings.jobRecordRealtimeBandwidthMaxInstances",
        descriptionKey: "settings.jobRecordRealtimeBandwidthMaxInstancesHelp",
        inputType: "number",
        requiresRestart: true,
      },
      {
        key: "JOB_HWID_DEVICE_CLEANUP_INTERVAL",
        labelKey: "settings.jobHwidDeviceCleanupInterval",
        descriptionKey: "settings.jobHwidDeviceCleanupIntervalHelp",
        inputType: "number",
        requiresRestart: true,
      },
    ],
  },
  {
    id: "notifications",
    titleKey: "settings.groups.notifications",
    settings: [
      {
        key: "NOTIFY_STATUS_CHANGE",
        labelKey: "settings.notifyStatusChange",
        descriptionKey: "settings.notifyStatusChangeHelp",
        inputType: "boolean",
      },
      {
        key: "NOTIFY_USER_CREATED",
        labelKey: "settings.notifyUserCreated",
        descriptionKey: "settings.notifyUserCreatedHelp",
        inputType: "boolean",
      },
      {
        key: "NOTIFY_USER_UPDATED",
        labelKey: "settings.notifyUserUpdated",
        descriptionKey: "settings.notifyUserUpdatedHelp",
        inputType: "boolean",
      },
      {
        key: "NOTIFY_USER_DELETED",
        labelKey: "settings.notifyUserDeleted",
        descriptionKey: "settings.notifyUserDeletedHelp",
        inputType: "boolean",
      },
      {
        key: "NOTIFY_USER_DATA_USED_RESET",
        labelKey: "settings.notifyUserDataUsedReset",
        descriptionKey: "settings.notifyUserDataUsedResetHelp",
        inputType: "boolean",
      },
      {
        key: "NOTIFY_USER_SUB_REVOKED",
        labelKey: "settings.notifyUserSubRevoked",
        descriptionKey: "settings.notifyUserSubRevokedHelp",
        inputType: "boolean",
      },
      {
        key: "NOTIFY_IF_DATA_USAGE_PERCENT_REACHED",
        labelKey: "settings.notifyUsagePercentReached",
        descriptionKey: "settings.notifyUsagePercentReachedHelp",
        inputType: "boolean",
      },
      {
        key: "NOTIFY_IF_DAYS_LEFT_REACHED",
        labelKey: "settings.notifyDaysLeftReached",
        descriptionKey: "settings.notifyDaysLeftReachedHelp",
        inputType: "boolean",
      },
      {
        key: "NOTIFY_LOGIN",
        labelKey: "settings.notifyLogin",
        descriptionKey: "settings.notifyLoginHelp",
        inputType: "boolean",
      },
      {
        key: "NOTIFY_REACHED_USAGE_PERCENT",
        labelKey: "settings.notifyReachedUsagePercent",
        descriptionKey: "settings.notifyReachedUsagePercentHelp",
        inputType: "textarea",
        delimiter: ",",
      },
      {
        key: "NOTIFY_DAYS_LEFT",
        labelKey: "settings.notifyDaysLeft",
        descriptionKey: "settings.notifyDaysLeftHelp",
        inputType: "textarea",
        delimiter: ",",
      },
      {
        key: "RECURRENT_NOTIFICATIONS_TIMEOUT",
        labelKey: "settings.recurrentNotificationsTimeout",
        descriptionKey: "settings.recurrentNotificationsTimeoutHelp",
        inputType: "number",
      },
      {
        key: "NUMBER_OF_RECURRENT_NOTIFICATIONS",
        labelKey: "settings.numberOfRecurrentNotifications",
        descriptionKey: "settings.numberOfRecurrentNotificationsHelp",
        inputType: "number",
      },
    ],
  },
  {
    id: "webhooks",
    titleKey: "settings.groups.webhooks",
    settings: [
      {
        key: "WEBHOOK_ADDRESS",
        labelKey: "settings.webhookAddress",
        descriptionKey: "settings.webhookAddressHelp",
        inputType: "textarea",
        delimiter: ",",
      },
      {
        key: "DISCORD_WEBHOOK_URL",
        labelKey: "settings.discordWebhookUrl",
        descriptionKey: "settings.discordWebhookUrlHelp",
        inputType: "text",
      },
    ],
  },
];
