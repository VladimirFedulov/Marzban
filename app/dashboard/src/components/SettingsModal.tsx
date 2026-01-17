import {
  Badge,
  Box,
  Button,
  Divider,
  Flex,
  FormControl,
  FormLabel,
  Heading,
  HStack,
  IconButton,
  Input,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalHeader,
  ModalOverlay,
  Select,
  SimpleGrid,
  Stack,
  Switch,
  Tag,
  Text,
  Textarea,
  Tooltip,
  Wrap,
  WrapItem,
  useColorModeValue,
  useToast,
} from "@chakra-ui/react";
import {
  PlusIcon,
  QuestionMarkCircleIcon,
  TrashIcon,
} from "@heroicons/react/24/outline";
import { useDashboard } from "contexts/DashboardContext";
import {
  SettingDefinition,
  settingsGroups,
} from "constants/AdminSettings";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { useMutation, useQuery, useQueryClient } from "react-query";
import { useLocation, useNavigate } from "react-router-dom";
import { fetch } from "service/http";

type SettingsResponse = {
  values: Record<string, unknown>;
  metadata: Record<string, { requires_restart: boolean }>;
};

type CustomHeaderRule = {
  name: string;
  value: string;
  user_agent: string;
};

type SettingsPayload = {
  values: Record<string, unknown>;
};

type DraftValue = string | boolean | CustomHeaderRule[];

const formatSettingValue = (
  setting: SettingDefinition,
  value: unknown
): DraftValue => {
  if (setting.inputType === "boolean") {
    return Boolean(value);
  }
  if (setting.inputType === "textarea") {
    if (Array.isArray(value)) {
      return value.join(`${setting.delimiter ?? ","} `);
    }
    return value ? String(value) : "";
  }
  if (setting.key === "SUBSCRIPTION_CUSTOM_HEADERS") {
    if (!Array.isArray(value)) return [];
    return value
      .filter((entry): entry is Record<string, unknown> => Boolean(entry))
      .map((entry) => ({
        name: entry.name ? String(entry.name) : "",
        value: entry.value ? String(entry.value) : "",
        user_agent: entry.user_agent ? String(entry.user_agent) : "",
      }));
  }
  return value ? String(value) : "";
};

const parseListValue = (raw: string, delimiter: string): string[] => {
  if (!raw) return [];
  return raw
    .split(delimiter)
    .map((item) => item.trim())
    .filter(Boolean);
};

export const SettingsModal = () => {
  const { isEditingSettings, onEditingSettings } = useDashboard();
  const { t } = useTranslation();
  const toast = useToast();
  const queryClient = useQueryClient();
  const cardBg = useColorModeValue("white", "gray.800");
  const cardBorder = useColorModeValue("gray.200", "whiteAlpha.200");
  const cardShadow = useColorModeValue("sm", "md");
  const groupTitleColor = useColorModeValue("gray.700", "gray.100");
  const labelColor = useColorModeValue("gray.600", "gray.300");
  const helperTextColor = useColorModeValue("gray.600", "gray.400");
  const inputBg = useColorModeValue("white", "whiteAlpha.100");
  const inputBorder = useColorModeValue("gray.200", "whiteAlpha.300");
  const inputHoverBorder = useColorModeValue("gray.300", "whiteAlpha.400");
  const inputFocusBorder = useColorModeValue("blue.400", "blue.300");
  const location = useLocation();
  const navigate = useNavigate();
  const envOnlySettings = [
    "DASHBOARD_PATH",
    "XRAY_JSON",
    "XRAY_EXECUTABLE_PATH",
    "XRAY_ASSETS_PATH",
    "XRAY_EXCLUDE_INBOUND_TAGS",
    "XRAY_FALLBACKS_INBOUND_TAG",
    "UVICORN_HOST",
    "UVICORN_PORT",
    "UVICORN_UDS",
    "UVICORN_SSL_CERTFILE",
    "UVICORN_SSL_KEYFILE",
    "UVICORN_SSL_CA_TYPE",
    "ALLOWED_ORIGINS",
    "SQLALCHEMY_DATABASE_URL",
    "SQLALCHEMY_POOL_SIZE",
    "SQLIALCHEMY_MAX_OVERFLOW",
    "TELEGRAM_API_TOKEN",
    "TELEGRAM_ADMIN_ID",
    "TELEGRAM_LOGGER_CHANNEL_ID",
    "TELEGRAM_LOGGER_TOPIC_ID",
    "TELEGRAM_DEFAULT_VLESS_FLOW",
    "TELEGRAM_PROXY_URL",
    "LOGIN_NOTIFY_WHITE_LIST",
    "WEBHOOK_SECRET",
    "VITE_BASE_API",
    "JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
    "DEBUG",
    "DOCS",
    "DISABLE_RECORDING_NODE_USAGE",
    "SUDO_USERNAME",
    "SUDO_PASSWORD",
  ];

  const { data, isLoading } = useQuery<SettingsResponse>({
    queryKey: ["settings"],
    queryFn: () => fetch("/settings"),
    enabled: isEditingSettings,
  });
  const [draftValues, setDraftValues] = useState<Record<string, DraftValue>>({});

  useEffect(() => {
    if (!data?.values) return;
    const initialValues: Record<string, DraftValue> = {};
    settingsGroups.forEach((group) => {
      group.settings.forEach((setting) => {
        initialValues[setting.key] = formatSettingValue(
          setting,
          data.values[setting.key]
        );
      });
    });
    setDraftValues(initialValues);
  }, [data]);

  const { mutate: saveSettings, isLoading: isSaving } = useMutation({
    mutationFn: (payload: SettingsPayload) =>
      fetch("/settings", {
        method: "PUT",
        body: payload,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries(["settings"]);
      toast({
        title: t("settings.saved"),
        status: "success",
        duration: 3000,
        isClosable: true,
      });
    },
    onError: (error: Error) => {
      toast({
        title: t("settings.saveError"),
        description: error.message,
        status: "error",
        duration: 4000,
        isClosable: true,
      });
    },
  });

  const sanitizeCustomHeaders = (
    headers: DraftValue
  ): CustomHeaderRule[] => {
    if (!Array.isArray(headers)) return [];
    return headers
      .map((header) => ({
        name: header.name.trim(),
        value: header.value.trim(),
        user_agent: header.user_agent.trim(),
      }))
      .filter((header) => header.name && header.value);
  };

  const handleSave = () => {
    const payload: SettingsPayload = { values: {} };
    settingsGroups.forEach((group) => {
      group.settings.forEach((setting) => {
        const rawValue = draftValues[setting.key];
        if (setting.inputType === "boolean") {
          payload.values[setting.key] = Boolean(rawValue);
          return;
        }
        if (setting.inputType === "number") {
          payload.values[setting.key] = Number(rawValue);
          return;
        }
        if (setting.inputType === "textarea") {
          payload.values[setting.key] = parseListValue(
            String(rawValue ?? ""),
            setting.delimiter ?? ","
          );
          return;
        }
        if (setting.inputType === "custom") {
          payload.values[setting.key] = sanitizeCustomHeaders(rawValue);
          return;
        }
        payload.values[setting.key] = String(rawValue ?? "");
      });
    });
    saveSettings(payload);
  };

  const renderCustomHeaders = (
    value: DraftValue,
    onChange: (nextValue: CustomHeaderRule[]) => void,
    isDisabled?: boolean
  ) => {
    const headers = Array.isArray(value) ? value : [];
    const updateHeader = (
      index: number,
      key: keyof CustomHeaderRule,
      nextValue: string
    ) => {
      onChange(
        headers.map((header, idx) =>
          idx === index ? { ...header, [key]: nextValue } : header
        )
      );
    };
    const handleAdd = () =>
      onChange([...headers, { name: "", value: "", user_agent: "" }]);
    const handleRemove = (index: number) =>
      onChange(headers.filter((_, idx) => idx !== index));

    return (
      <Stack spacing={3}>
        <Stack spacing={2}>
          <Flex
            gap={4}
            fontSize="xs"
            textTransform="uppercase"
            color={labelColor}
            fontWeight="semibold"
          >
            <Box flex="1">{t("settings.subscriptionCustomHeadersName")}</Box>
            <Box flex="1">{t("settings.subscriptionCustomHeadersValue")}</Box>
            <Box flex="1">{t("settings.subscriptionCustomHeadersUserAgent")}</Box>
            <Box w="36px" />
          </Flex>
          <Divider borderColor={cardBorder} />
        </Stack>
        {headers.length === 0 ? (
          <Text fontSize="sm" color={helperTextColor}>
            {t("settings.subscriptionCustomHeadersEmpty")}
          </Text>
        ) : (
          <Stack spacing={2}>
            {headers.map((header, index) => (
              <HStack key={`${header.name}-${index}`} align="flex-start">
                <Input
                  flex="1"
                  bg={inputBg}
                  borderColor={inputBorder}
                  _hover={{ borderColor: inputHoverBorder }}
                  _focusVisible={{
                    borderColor: inputFocusBorder,
                    boxShadow: "none",
                  }}
                  placeholder={t(
                    "settings.subscriptionCustomHeadersNamePlaceholder"
                  )}
                  value={header.name}
                  onChange={(event) =>
                    updateHeader(index, "name", event.target.value)
                  }
                  isDisabled={isDisabled}
                />
                <Input
                  flex="1"
                  bg={inputBg}
                  borderColor={inputBorder}
                  _hover={{ borderColor: inputHoverBorder }}
                  _focusVisible={{
                    borderColor: inputFocusBorder,
                    boxShadow: "none",
                  }}
                  placeholder={t(
                    "settings.subscriptionCustomHeadersValuePlaceholder"
                  )}
                  value={header.value}
                  onChange={(event) =>
                    updateHeader(index, "value", event.target.value)
                  }
                  isDisabled={isDisabled}
                />
                <Input
                  flex="1"
                  bg={inputBg}
                  borderColor={inputBorder}
                  _hover={{ borderColor: inputHoverBorder }}
                  _focusVisible={{
                    borderColor: inputFocusBorder,
                    boxShadow: "none",
                  }}
                  placeholder={t(
                    "settings.subscriptionCustomHeadersUserAgentPlaceholder"
                  )}
                  value={header.user_agent}
                  onChange={(event) =>
                    updateHeader(index, "user_agent", event.target.value)
                  }
                  isDisabled={isDisabled}
                />
                <IconButton
                  aria-label={t("settings.subscriptionCustomHeadersRemove")}
                  icon={<TrashIcon width={16} />}
                  size="sm"
                  variant="ghost"
                  colorScheme="red"
                  onClick={() => handleRemove(index)}
                  isDisabled={isDisabled}
                />
              </HStack>
            ))}
          </Stack>
        )}
        <Button
          size="sm"
          variant="outline"
          leftIcon={<PlusIcon width={16} />}
          onClick={handleAdd}
          isDisabled={isDisabled}
          alignSelf="flex-start"
        >
          {t("settings.subscriptionCustomHeadersAdd")}
        </Button>
      </Stack>
    );
  };

  const renderInput = (setting: SettingDefinition) => {
    const value = draftValues[setting.key];
    if (setting.inputType === "boolean") {
      return (
        <Switch
          isChecked={Boolean(value)}
          colorScheme="blue"
          onChange={(event) =>
            setDraftValues((prev) => ({
              ...prev,
              [setting.key]: event.target.checked,
            }))
          }
        />
      );
    }
    if (setting.inputType === "number") {
      return (
        <Input
          type="number"
          bg={inputBg}
          borderColor={inputBorder}
          _hover={{ borderColor: inputHoverBorder }}
          _focusVisible={{ borderColor: inputFocusBorder, boxShadow: "none" }}
          value={String(value ?? "")}
          onChange={(event) =>
            setDraftValues((prev) => ({
              ...prev,
              [setting.key]: event.target.value,
            }))
          }
        />
      );
    }
    if (setting.inputType === "textarea") {
      return (
        <Textarea
          bg={inputBg}
          borderColor={inputBorder}
          _hover={{ borderColor: inputHoverBorder }}
          _focusVisible={{ borderColor: inputFocusBorder, boxShadow: "none" }}
          value={String(value ?? "")}
          onChange={(event) =>
            setDraftValues((prev) => ({
              ...prev,
              [setting.key]: event.target.value,
            }))
          }
        />
      );
    }
    if (setting.inputType === "select") {
      return (
        <Select
          bg={inputBg}
          borderColor={inputBorder}
          _hover={{ borderColor: inputHoverBorder }}
          _focusVisible={{ borderColor: inputFocusBorder, boxShadow: "none" }}
          value={String(value ?? "")}
          onChange={(event) =>
            setDraftValues((prev) => ({
              ...prev,
              [setting.key]: event.target.value,
            }))
          }
        >
          {setting.options?.map((option) => (
            <option key={option.value} value={option.value}>
              {t(option.labelKey)}
            </option>
          ))}
        </Select>
      );
    }
    if (setting.inputType === "custom") {
      return renderCustomHeaders(value, (nextValue) =>
        setDraftValues((prev) => ({
          ...prev,
          [setting.key]: nextValue,
        }))
      );
    }
    return (
      <Input
        type="text"
        bg={inputBg}
        borderColor={inputBorder}
        _hover={{ borderColor: inputHoverBorder }}
        _focusVisible={{ borderColor: inputFocusBorder, boxShadow: "none" }}
        value={String(value ?? "")}
        onChange={(event) =>
          setDraftValues((prev) => ({
            ...prev,
            [setting.key]: event.target.value,
          }))
        }
      />
    );
  };

  const renderGroup = (groupList: typeof settingsGroups) => (
    <Stack spacing={8}>
      {groupList.map((group) => (
        <Box
          key={group.id}
          borderWidth="1px"
          borderRadius="xl"
          p={{ base: 5, md: 6 }}
          bg={cardBg}
          borderColor={cardBorder}
          boxShadow={cardShadow}
        >
          <Stack spacing={5}>
            <Flex justify="space-between" align="center" flexWrap="wrap" gap={2}>
              <Heading size="sm" color={groupTitleColor}>
                {t(group.titleKey)}
              </Heading>
              <Badge variant="subtle" colorScheme="blue">
                {group.settings.length}
              </Badge>
            </Flex>
            {group.descriptionKey ? (
              <Text fontSize="sm" color={helperTextColor}>
                {t(group.descriptionKey)}
              </Text>
            ) : null}
            <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={5}>
              {group.settings.map((setting) => {
                const requiresRestart =
                  data?.metadata?.[setting.key]?.requires_restart ??
                  setting.requiresRestart;
                const isWide = setting.inputType === "custom";
                return (
                  <FormControl
                    key={setting.key}
                    isDisabled={isLoading}
                    gridColumn={isWide ? { base: "auto", lg: "1 / -1" } : undefined}
                  >
                    <Stack spacing={2}>
                      <Box>
                        <FormLabel
                          mb={1}
                          color={labelColor}
                          display="flex"
                          alignItems="center"
                          gap={2}
                        >
                          <Box as="span">{t(setting.labelKey)}</Box>
                          {setting.descriptionKey ? (
                            <Tooltip
                              label={t(setting.descriptionKey)}
                              placement="top"
                              hasArrow
                            >
                              <Box
                                as={QuestionMarkCircleIcon}
                                cursor="help"
                                w={4}
                                h={4}
                              />
                            </Tooltip>
                          ) : null}
                        </FormLabel>
                        {requiresRestart ? (
                          <Badge colorScheme="orange" variant="subtle">
                            {t("settings.restartRequired")}
                          </Badge>
                        ) : null}
                      </Box>
                      {renderInput(setting)}
                    </Stack>
                  </FormControl>
                );
              })}
            </SimpleGrid>
          </Stack>
        </Box>
      ))}
    </Stack>
  );

  const handleClose = () => {
    onEditingSettings(false);
    if (location.pathname === "/settings") {
      navigate("/");
    }
  };

  return (
    <Modal
      isOpen={isEditingSettings}
      onClose={handleClose}
      size="6xl"
      scrollBehavior="inside"
    >
      <ModalOverlay bg="blackAlpha.300" backdropFilter="blur(10px)" />
      <ModalContent mx="3" w="full" maxW="6xl">
        <ModalHeader pb={2} pr={{ base: 12, md: 16 }}>
          <Flex
            direction={{ base: "column", md: "row" }}
            align={{ base: "flex-start", md: "center" }}
            justify="space-between"
            gap={4}
          >
            <Box>
              <Heading size="md">{t("settings.title")}</Heading>
              <Text color={helperTextColor} fontSize="sm">
                {t("settings.description")}
              </Text>
            </Box>
            <Button
              colorScheme="blue"
              onClick={handleSave}
              isLoading={isSaving}
            >
              {t("settings.save")}
            </Button>
          </Flex>
        </ModalHeader>
        <ModalCloseButton />
        <ModalBody pb={6} pt={4}>
          <Stack spacing={6}>
            <Box>{renderGroup(settingsGroups)}</Box>
            <Box
              borderWidth="1px"
              borderRadius="xl"
              p={{ base: 5, md: 6 }}
              bg={cardBg}
              borderColor={cardBorder}
              boxShadow={cardShadow}
            >
              <Stack spacing={3}>
                <Heading size="sm" color={groupTitleColor}>
                  {t("settings.envOnlyTitle")}
                </Heading>
                <Text fontSize="sm" color={helperTextColor}>
                  {t("settings.envOnlyDescription")}
                </Text>
                <Wrap spacing={2}>
                  {envOnlySettings.map((setting) => (
                    <WrapItem key={setting}>
                      <Tag size="sm" variant="subtle" colorScheme="gray">
                        {setting}
                      </Tag>
                    </WrapItem>
                  ))}
                </Wrap>
              </Stack>
            </Box>
          </Stack>
        </ModalBody>
      </ModalContent>
    </Modal>
  );
};

export default SettingsModal;
