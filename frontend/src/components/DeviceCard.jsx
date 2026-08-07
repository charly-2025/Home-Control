import { Card, CardContent, Typography, Switch } from "@mui/material";

export default function DeviceCard({
    device,
    onToggle,
}) {
    return (
        <Card sx={{ width: 300 }}>
            <CardContent>

                <Typography variant="h6">
                    {device.friendly_name}
                </Typography>

                <Switch
                    checked={device.state === "ON"}
                    onChange={() => onToggle(device)}
                />

            </CardContent>
        </Card>
    );
}