import { useDashboard } from "contexts/DashboardContext";
import { useEffect } from "react";
import { Dashboard } from "./Dashboard";

export const Settings = () => {
  useEffect(() => {
    useDashboard.getState().onEditingSettings(true);
    return () => {
      useDashboard.getState().onEditingSettings(false);
    };
  }, []);

  return <Dashboard />;
};

export default Settings;
