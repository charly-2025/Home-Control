import {
  Box,
  Divider,
  Drawer,
  IconButton,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
} from "@mui/material";

import MenuIcon from "@mui/icons-material/Menu";
import MenuOpenIcon from "@mui/icons-material/MenuOpen";

import DashboardIcon from "@mui/icons-material/Dashboard";
import DevicesIcon from "@mui/icons-material/Devices";
import HomeIcon from "@mui/icons-material/Home";
import GroupWorkIcon from "@mui/icons-material/GroupWork";
import PersonIcon from "@mui/icons-material/Person";
import SettingsIcon from "@mui/icons-material/Settings";

import { Link, useLocation } from "react-router-dom";

export const DRAWER_WIDTH = 260;
export const DRAWER_WIDTH_COLLAPSED = 72;

const navigation = [
  {
    title: "Dashboard",
    path: "/",
    icon: <DashboardIcon />,
  },
  {
    title: "Devices",
    path: "/devices",
    icon: <DevicesIcon />,
  },
  {
    title: "Rooms",
    path: "/rooms",
    icon: <HomeIcon />,
  },
  {
    title: "Groups",
    path: "/groups",
    icon: <GroupWorkIcon />,
  },
];

const bottomNavigation = [
  {
    title: "Settings",
    path: "/settings",
    icon: <SettingsIcon />,
  },
  {
    title: "Account",
    path: "/account",
    icon: <PersonIcon />,
  },
];

// Largeur de la colonne "icône" : FIXE, jamais animée.
// C'est ce qui garantit que les icônes ne bougent jamais,
// ni entre les états open/closed, ni pendant la transition.
const ICON_COLUMN_WIDTH = DRAWER_WIDTH_COLLAPSED;

function NavItem({ page, open, selected }) {
  return (
    <ListItemButton
      component={Link}
      to={page.path}
      selected={selected}
      sx={{
        minHeight: 52,
        display: "flex",
        alignItems: "center",
        // Plus de justifyContent: "center" ici : c'est justement ça qui
        // faisait bouger la colonne icône quand sa largeur changeait.
        px: 0,
      }}
    >
      <ListItemIcon
        sx={{
          width: ICON_COLUMN_WIDTH,
          minWidth: ICON_COLUMN_WIDTH,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          flexShrink: 0,
        }}
      >
        {page.icon}
      </ListItemIcon>

      <ListItemText
        primary={page.title}
        slotProps={{
          primary: {
            noWrap: true,
            fontWeight: 500,
          },
        }}
        sx={{
          m: 0,
          overflow: "hidden",
          whiteSpace: "nowrap",
          width: open ? DRAWER_WIDTH - ICON_COLUMN_WIDTH : 0,
          opacity: open ? 1 : 0,
          transition: (theme) =>
            theme.transitions.create(["width", "opacity"], {
              duration: 250,
            }),
        }}
      />
    </ListItemButton>
  );
}

export default function Sidebar({ open, toggleSidebar }) {
  const location = useLocation();

  const drawerWidth = open ? DRAWER_WIDTH : DRAWER_WIDTH_COLLAPSED;

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        transition: (theme) =>
          theme.transitions.create("width", {
            easing: theme.transitions.easing.easeInOut,
            duration: 300,
          }),
        "& .MuiDrawer-paper": {
          width: drawerWidth,
          overflowX: "hidden",
          transition: (theme) =>
            theme.transitions.create("width", {
              easing: theme.transitions.easing.easeInOut,
              duration: 300,
            }),
          boxSizing: "border-box",
          borderRight: 1,
          borderColor: "divider",
        },
      }}
    >
      <Toolbar
        disableGutters
        sx={{
          minHeight: 64,
          borderBottom: 1,
          borderColor: "divider",
          px: 0,
          display: "flex",
          alignItems: "center",
        }}
      >
        {/* Même logique que pour les items : colonne fixe pour le bouton */}
        <Box
          sx={{
            width: ICON_COLUMN_WIDTH,
            minWidth: ICON_COLUMN_WIDTH,
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            flexShrink: 0,
          }}
        >
          <IconButton
            onClick={toggleSidebar}
            sx={{
              width: 40,
              height: 40,
              p: 0,
            }}
          >
            {open ? <MenuOpenIcon /> : <MenuIcon />}
          </IconButton>
        </Box>

        <Typography
          variant="h6"
          sx={{
            overflow: "hidden",
            whiteSpace: "nowrap",
            width: open ? DRAWER_WIDTH - ICON_COLUMN_WIDTH : 0,
            opacity: open ? 1 : 0,
            transition: (theme) =>
              theme.transitions.create(["width", "opacity"], {
                duration: 250,
              }),
          }}
        >
          Home Control
        </Typography>
      </Toolbar>

      <Box
        sx={{
          display: "flex",
          flexDirection: "column",
          height: "100%",
        }}
      >
        <List disablePadding>
          {navigation.map((page) => (
            <NavItem
              key={page.path}
              page={page}
              open={open}
              selected={location.pathname === page.path}
            />
          ))}
        </List>

        <Box sx={{ flexGrow: 1 }} />

        <Divider />
        <List disablePadding>
          {bottomNavigation.map((page) => (
            <NavItem
              key={page.path}
              page={page}
              open={open}
              selected={location.pathname === page.path}
            />
          ))}
        </List>
      </Box>
    </Drawer>
  );
}