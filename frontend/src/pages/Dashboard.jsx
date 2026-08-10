import {
    Box,
    Card,
    Typography,
    Switch,
    useMediaQuery,
    useTheme,
} from "@mui/material";

import OutletIcon from "@mui/icons-material/Outlet";

import { useDevices } from "../context/DevicesContext";

const DESKTOP_COLUMNS = 5;
const DESKTOP_ROWS = 6;
const MOBILE_COLUMNS = 2;
const MOBILE_ROWS = 8;

export default function Dashboard() {
    const theme = useTheme();
    const isDesktop = useMediaQuery(theme.breakpoints.up("sm"));

    const { devices, toggleDevice } = useDevices();

    const columns = isDesktop ? DESKTOP_COLUMNS : MOBILE_COLUMNS;
    const rows = isDesktop ? DESKTOP_ROWS : MOBILE_ROWS;
    const cellCount = columns * rows;

    return (
        <Box
            sx={{
                height: "calc(100vh - 64px)",
                boxSizing: "border-box",
                display: "grid",
                gap: 2,
                p: 2,
                gridTemplateColumns: `repeat(${columns}, 1fr)`,
                gridTemplateRows: `repeat(${rows}, 1fr)`,
                bgcolor: "background.default",
            }}
        >
            {Array.from({ length: cellCount }, (_, index) => {
                const device = devices[index];
                const isOn = device?.state === "ON";

                if (!device) {
                    return (
                        <Box
                            key={index}
                            sx={{
                                minHeight: 0,
                                minWidth: 0,
                                borderRadius: "16px",
                                border: "2px dashed",
                                borderColor: "divider",
                            }}
                        />
                    );
                }

                return (
                    <Card
                        key={device.friendly_name}
                        elevation={0}
                        sx={{
                            height: "100%",
                            width: "100%",
                            minHeight: 0,
                            minWidth: 0,
                            boxSizing: "border-box",
                            borderRadius: "16px",
                            border: "2px solid",
                            borderColor: isOn ? "warning.main" : "divider",
                            display: "flex",
                            flexDirection: "column",
                            justifyContent: "space-between",
                            p: 2,
                            overflow: "hidden",
                        }}
                    >
                        <Box sx={{ display: "flex", alignItems: "center", gap: 1.5 }}>
                            <OutletIcon
                                color={isOn ? "warning" : "disabled"}
                                sx={{ fontSize: 32 }}
                            />

                            <Typography variant="subtitle1" fontWeight={600} noWrap>
                                {device.friendly_name}
                            </Typography>
                        </Box>

                        {device.device_type === "switch" && (
                            <Box
                                sx={{
                                    display: "flex",
                                    alignItems: "center",
                                    justifyContent: "space-between",
                                }}
                            >
                                <Typography
                                    variant="body2"
                                    color={isOn ? "warning.main" : "text.secondary"}
                                    fontWeight={600}
                                >
                                    {isOn ? "Allumé" : "Éteint"}
                                </Typography>

                                <Switch
                                    checked={isOn}
                                    color="warning"
                                    onChange={() => toggleDevice(device)}
                                />
                            </Box>
                        )}
                    </Card>
                );
            })}
        </Box>
    );
}
