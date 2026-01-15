import {
  Badge,
  Box,
  Button,
  Flex,
  FormControl,
  FormLabel,
  Heading,
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
  Text,
  Textarea,
  useColorModeValue,
  useToast,
} from "@chakra-ui/react";
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

type SettingsPayload = {
  values: Record<string, unknown>;
};

const formatSettingValue = (
  setting: SettingDefinition,
  value: unknown
): string | boolean => {
  if (setting.inputType === "boolean") {
    return Boolean(value);
  }
  if (setting.inputType === "textarea") {
    if (Array.isArray(value)) {
      return value.join(`${setting.delimiter ?? ","} `);
    }
    return value ? String(value) : "";
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

  const { data, isLoading } = useQuery<SettingsResponse>({
    queryKey: ["settings"],
    queryFn: () => fetch("/settings"),
    enabled: isEditingSettings,
  });
  const [draftValues, setDraftValues] = useState<
    Record<string, string | boolean>
  >({});

  useEffect(() => {
    if (!data?.values) return;
    const initialValues: Record<string, string | boolean> = {};
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
        payload.values[setting.key] = String(rawValue ?? "");
      });
    });
    saveSettings(payload);
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
            <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={5}>
              {group.settings.map((setting) => {
                const requiresRestart =
                  data?.metadata?.[setting.key]?.requires_restart ??
                  setting.requiresRestart;
                return (
                  <FormControl key={setting.key} isDisabled={isLoading}>
                    <Stack spacing={2}>
                      <Box>
                        <FormLabel mb={1} color={labelColor}>
                          {t(setting.labelKey)}
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
        <ModalHeader pb={2}>
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
            <Flex justify="flex-end">
              <Button
                colorScheme="blue"
                onClick={handleSave}
                isLoading={isSaving}
              >
                {t("settings.save")}
              </Button>
            </Flex>
          </Stack>
        </ModalBody>
      </ModalContent>
    </Modal>
  );
};

export default SettingsModal;
