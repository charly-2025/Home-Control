import { useEffect, useMemo, useState } from "react";
import { Outlet, useLocation } from "react-router-dom";

import { AppBar, Box, Toolbar, Typography } from "@mui/material";

import Sidebar, {
  DRAWER_WIDTH,
  DRAWER_WIDTH_COLLAPSED,
} from "../components/Sidebar";

import { connect, disconnect } from "../websocket/socket";

const PAGE_TITLES = {
  "/": "Dashboard",
  "/devices": "Devices",
  "/rooms": "Rooms",
  "/groups": "Groups",
  "/account": "Account",
  "/settings": "Settings",
};

export default function MainLayout() {
  const location = useLocation();

  const [sidebarOpen, setSidebarOpen] = useState(true);

  useEffect(() => {
    connect((message) => {
      console.log(message);
    });

    return () => {
      disconnect();
    };
  }, []);

  const drawerWidth = sidebarOpen ? DRAWER_WIDTH : DRAWER_WIDTH_COLLAPSED;

  const pageTitle = useMemo(() => {
    return PAGE_TITLES[location.pathname] ?? "";
  }, [location.pathname]);

  return (
    <Box
      sx={{
        display: "flex",
        minHeight: "100vh",
        bgcolor: "background.default",
      }}
    >
      <Sidebar
        open={sidebarOpen}
        toggleSidebar={() => setSidebarOpen(!sidebarOpen)}
      />

      <Box
        sx={{
          flexGrow: 1,
          display: "flex",
          flexDirection: "column",
        }}
      >
        <AppBar
          position="fixed"
          color="inherit"
          elevation={0}
          sx={{
            left: drawerWidth,
            width: `calc(100% - ${drawerWidth}px)`,
            transition: (theme) =>
              theme.transitions.create(["left", "width"], {
                easing: theme.transitions.easing.easeInOut,
                duration: 300,
              }),
            borderBottom: 1,
            borderColor: "divider",
          }}
        >
          <Toolbar
            sx={{
              minHeight: 64,
            }}
          >
            <Typography variant="h5" fontWeight={600}>
              {pageTitle}
            </Typography>
          </Toolbar>
        </AppBar>

        <Toolbar
          sx={{
            minHeight: 64,
          }}
        />

        <Box
          component="main"
          sx={{
            flexGrow: 1,
            overflow: "auto",
            p: 3,
            transition: (theme) =>
              theme.transitions.create(["margin", "width"], {
                easing: theme.transitions.easing.easeInOut,
                duration: 300,
              }),
          }}
        >
          <Outlet />
        </Box>
      </Box>
    </Box>
  );
}
