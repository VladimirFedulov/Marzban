import {
  Badge,
  Box,
  Button,
  Container,
  Flex,
  FormControl,
  FormLabel,
  Heading,
  Input,
  Select,
  SimpleGrid,
  Stack,
  Switch,
  Text,
  Textarea,
  useToast,
  VStack,
} from "@chakra-ui/react";
import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "react-query";
import { useTranslation } from "react-i18next";
import { Header } from "components/Header";
import { Footer } from "components/Footer";
import {
  SettingDefinition,
  settingsGroups,
} from "constants/AdminSettings";
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

export const Settings = () => {
  const { t } = useTranslation();
  const toast = useToast();
  const queryClient = useQueryClient();
  const { data, isLoading } = useQuery<SettingsResponse>({
    queryKey: ["settings"],
    queryFn: () => fetch("/settings"),
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
          bg="chakra-body-bg"
          boxShadow="sm"
        >
          <Stack spacing={5}>
            <Flex justify="space-between" align="center" flexWrap="wrap" gap={2}>
              <Heading size="sm">{t(group.titleKey)}</Heading>
              <Badge variant="subtle" colorScheme="gray">
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
                        <FormLabel mb={1}>{t(setting.labelKey)}</FormLabel>
                        {requiresRestart ? (
                          <Badge colorScheme="orange">
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

  return (
    <VStack justifyContent="space-between" minH="100vh" rowGap={4}>
      <Box w="full" py={{ base: 6, md: 8 }}>
        <Container maxW="6xl">
          <Header title={t("settings.title")} />
          <Stack spacing={6} mt={6}>
            <Flex
              direction={{ base: "column", md: "row" }}
              align={{ base: "flex-start", md: "center" }}
              justify="space-between"
              gap={4}
            >
              <Box>
                <Heading size="md">{t("settings.title")}</Heading>
                <Text color="gray.500">{t("settings.description")}</Text>
              </Box>
              <Button
                colorScheme="blue"
                onClick={handleSave}
                isLoading={isSaving}
              >
                {t("settings.save")}
              </Button>
            </Flex>
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
        </Container>
      </Box>
      <Footer />
    </VStack>
  );
};

export default Settings;
