export type SettingInputType =
  | "boolean"
  | "number"
  | "text"
  | "textarea"
  | "select";

export type SettingOption = {
  value: string;
  labelKey: string;
};

export type SettingDefinition = {
  key: string;
  labelKey: string;
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
    id: "notifications",
    titleKey: "settings.groups.notifications",
    settings: [
      {
        key: "NOTIFY_STATUS_CHANGE",
        labelKey: "settings.notifyStatusChange",
        inputType: "boolean",
      },
      {
        key: "NOTIFY_USER_CREATED",
        labelKey: "settings.notifyUserCreated",
        inputType: "boolean",
      },
      {
        key: "NOTIFY_USER_UPDATED",
        labelKey: "settings.notifyUserUpdated",
        inputType: "boolean",
      },
      {
        key: "NOTIFY_USER_DELETED",
        labelKey: "settings.notifyUserDeleted",
        inputType: "boolean",
      },
      {
        key: "NOTIFY_USER_DATA_USED_RESET",
        labelKey: "settings.notifyUserDataUsedReset",
        inputType: "boolean",
      },
      {
        key: "NOTIFY_USER_SUB_REVOKED",
        labelKey: "settings.notifyUserSubRevoked",
        inputType: "boolean",
      },
      {
        key: "NOTIFY_IF_DATA_USAGE_PERCENT_REACHED",
        labelKey: "settings.notifyUsagePercentReached",
        inputType: "boolean",
      },
      {
        key: "NOTIFY_IF_DAYS_LEFT_REACHED",
        labelKey: "settings.notifyDaysLeftReached",
        inputType: "boolean",
      },
      {
        key: "NOTIFY_LOGIN",
        labelKey: "settings.notifyLogin",
        inputType: "boolean",
      },
      {
        key: "NOTIFY_REACHED_USAGE_PERCENT",
        labelKey: "settings.notifyReachedUsagePercent",
        inputType: "textarea",
        delimiter: ",",
      },
      {
        key: "NOTIFY_DAYS_LEFT",
        labelKey: "settings.notifyDaysLeft",
        inputType: "textarea",
        delimiter: ",",
      },
      {
        key: "RECURRENT_NOTIFICATIONS_TIMEOUT",
        labelKey: "settings.recurrentNotificationsTimeout",
        inputType: "number",
      },
      {
        key: "NUMBER_OF_RECURRENT_NOTIFICATIONS",
        labelKey: "settings.numberOfRecurrentNotifications",
        inputType: "number",
      },
    ],
  },
  {
    id: "status-texts",
    titleKey: "settings.groups.statusTexts",
    settings: [
      {
        key: "ACTIVE_STATUS_TEXT",
        labelKey: "settings.activeStatusText",
        inputType: "text",
      },
      {
        key: "EXPIRED_STATUS_TEXT",
        labelKey: "settings.expiredStatusText",
        inputType: "text",
      },
      {
        key: "LIMITED_STATUS_TEXT",
        labelKey: "settings.limitedStatusText",
        inputType: "text",
      },
      {
        key: "DISABLED_STATUS_TEXT",
        labelKey: "settings.disabledStatusText",
        inputType: "text",
      },
      {
        key: "ONHOLD_STATUS_TEXT",
        labelKey: "settings.onHoldStatusText",
        inputType: "text",
      },
      {
        key: "USERS_AUTODELETE_DAYS",
        labelKey: "settings.usersAutodeleteDays",
        inputType: "number",
      },
      {
        key: "USER_AUTODELETE_INCLUDE_LIMITED_ACCOUNTS",
        labelKey: "settings.userAutodeleteIncludeLimitedAccounts",
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
        inputType: "text",
      },
      {
        key: "SUB_SUPPORT_URL",
        labelKey: "settings.subSupportUrl",
        inputType: "text",
      },
      {
        key: "SUB_PROFILE_TITLE",
        labelKey: "settings.subProfileTitle",
        inputType: "text",
      },
      {
        key: "SUBSCRIPTION_HIDE_DEFAULT_HOSTS_WHEN_CUSTOM_HOSTS",
        labelKey: "settings.subscriptionHideDefaultHosts",
        inputType: "boolean",
      },
      {
        key: "SUBSCRIPTION_CUSTOM_NOTES_EXPIRED",
        labelKey: "settings.subscriptionCustomNotesExpired",
        inputType: "textarea",
        delimiter: "|",
      },
      {
        key: "SUBSCRIPTION_CUSTOM_NOTES_LIMITED",
        labelKey: "settings.subscriptionCustomNotesLimited",
        inputType: "textarea",
        delimiter: "|",
      },
      {
        key: "SUBSCRIPTION_CUSTOM_NOTES_DISABLED",
        labelKey: "settings.subscriptionCustomNotesDisabled",
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
        inputType: "number",
      },
      {
        key: "HWID_DEVICE_RETENTION_DAYS",
        labelKey: "settings.hwidDeviceRetentionDays",
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
        inputType: "text",
      },
      {
        key: "SUBSCRIPTION_PAGE_TEMPLATE",
        labelKey: "settings.subscriptionPageTemplate",
        inputType: "text",
      },
      {
        key: "HOME_PAGE_TEMPLATE",
        labelKey: "settings.homePageTemplate",
        inputType: "text",
      },
      {
        key: "CLASH_SUBSCRIPTION_TEMPLATE",
        labelKey: "settings.clashSubscriptionTemplate",
        inputType: "text",
      },
      {
        key: "CLASH_SETTINGS_TEMPLATE",
        labelKey: "settings.clashSettingsTemplate",
        inputType: "text",
      },
      {
        key: "SINGBOX_SUBSCRIPTION_TEMPLATE",
        labelKey: "settings.singboxSubscriptionTemplate",
        inputType: "text",
      },
      {
        key: "SINGBOX_SETTINGS_TEMPLATE",
        labelKey: "settings.singboxSettingsTemplate",
        inputType: "text",
      },
      {
        key: "MUX_TEMPLATE",
        labelKey: "settings.muxTemplate",
        inputType: "text",
      },
      {
        key: "V2RAY_SUBSCRIPTION_TEMPLATE",
        labelKey: "settings.v2raySubscriptionTemplate",
        inputType: "text",
      },
      {
        key: "V2RAY_SETTINGS_TEMPLATE",
        labelKey: "settings.v2raySettingsTemplate",
        inputType: "text",
      },
      {
        key: "V2RAY_TEMPLATE_MAPPING",
        labelKey: "settings.v2rayTemplateMapping",
        inputType: "text",
      },
      {
        key: "EXTERNAL_CONFIG",
        labelKey: "settings.externalConfig",
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
        inputType: "text",
      },
      {
        key: "XRAY_SUBSCRIPTION_PATH",
        labelKey: "settings.xraySubscriptionPath",
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
        inputType: "boolean",
      },
      {
        key: "USE_CUSTOM_JSON_FOR_V2RAYN",
        labelKey: "settings.useCustomJsonForV2rayn",
        inputType: "boolean",
      },
      {
        key: "USE_CUSTOM_JSON_FOR_V2RAYNG",
        labelKey: "settings.useCustomJsonForV2rayng",
        inputType: "boolean",
      },
      {
        key: "USE_CUSTOM_JSON_FOR_STREISAND",
        labelKey: "settings.useCustomJsonForStreisand",
        inputType: "boolean",
      },
      {
        key: "USE_CUSTOM_JSON_FOR_HAPP",
        labelKey: "settings.useCustomJsonForHapp",
        inputType: "boolean",
      },
      {
        key: "USE_CUSTOM_JSON_FOR_NPVTUNNEL",
        labelKey: "settings.useCustomJsonForNpvtunnel",
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
        inputType: "number",
        requiresRestart: true,
      },
      {
        key: "JOB_RECORD_NODE_USAGES_INTERVAL",
        labelKey: "settings.jobRecordNodeUsagesInterval",
        inputType: "number",
        requiresRestart: true,
      },
      {
        key: "JOB_RECORD_USER_USAGES_INTERVAL",
        labelKey: "settings.jobRecordUserUsagesInterval",
        inputType: "number",
        requiresRestart: true,
      },
      {
        key: "JOB_REVIEW_USERS_INTERVAL",
        labelKey: "settings.jobReviewUsersInterval",
        inputType: "number",
        requiresRestart: true,
      },
      {
        key: "JOB_SEND_NOTIFICATIONS_INTERVAL",
        labelKey: "settings.jobSendNotificationsInterval",
        inputType: "number",
        requiresRestart: true,
      },
      {
        key: "JOB_RECORD_REALTIME_BANDWIDTH_INTERVAL",
        labelKey: "settings.jobRecordRealtimeBandwidthInterval",
        inputType: "number",
        requiresRestart: true,
      },
      {
        key: "JOB_RECORD_USER_USAGES_WORKERS",
        labelKey: "settings.jobRecordUserUsagesWorkers",
        inputType: "number",
        requiresRestart: true,
      },
      {
        key: "JOB_CORE_HEALTH_CHECK_MAX_INSTANCES",
        labelKey: "settings.jobCoreHealthCheckMaxInstances",
        inputType: "number",
        requiresRestart: true,
      },
      {
        key: "JOB_RECORD_USER_USAGES_MAX_INSTANCES",
        labelKey: "settings.jobRecordUserUsagesMaxInstances",
        inputType: "number",
        requiresRestart: true,
      },
      {
        key: "JOB_RECORD_NODE_USAGES_MAX_INSTANCES",
        labelKey: "settings.jobRecordNodeUsagesMaxInstances",
        inputType: "number",
        requiresRestart: true,
      },
      {
        key: "JOB_RECORD_REALTIME_BANDWIDTH_MAX_INSTANCES",
        labelKey: "settings.jobRecordRealtimeBandwidthMaxInstances",
        inputType: "number",
        requiresRestart: true,
      },
      {
        key: "JOB_HWID_DEVICE_CLEANUP_INTERVAL",
        labelKey: "settings.jobHwidDeviceCleanupInterval",
        inputType: "number",
        requiresRestart: true,
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
        inputType: "textarea",
        delimiter: ",",
      },
      {
        key: "DISCORD_WEBHOOK_URL",
        labelKey: "settings.discordWebhookUrl",
        inputType: "text",
      },
    ],
  },
];
