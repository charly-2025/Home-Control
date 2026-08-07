import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";

import {
    Box,
    Button,
    Paper,
    TextField,
    Typography,
    Alert,
} from "@mui/material";

import { register } from "../api/auth";

export default function Register() {

    const navigate = useNavigate();

    const [firstName, setFirstName] = useState("");
    const [lastName, setLastName] = useState("");

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    const [error, setError] = useState("");

    async function handleSubmit(event) {

        event.preventDefault();

        setError("");

        try {

            await register({
                first_name: firstName,
                last_name: lastName,
                email,
                password,
            });

            navigate("/");

        } catch {

            setError("Unable to create account.");

        }

    }

    return (

        <Box
            sx={{
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                minHeight: "100vh",
                bgcolor: "#f5f5f5",
            }}
        >

            <Paper
                elevation={6}
                sx={{
                    p: 5,
                    width: 420,
                    borderRadius: 4,
                }}
            >

                <Typography
                    variant="h4"
                    align="center"
                    mb={4}
                >
                    Create account
                </Typography>

                {error && (
                    <Alert
                        severity="error"
                        sx={{ mb: 2 }}
                    >
                        {error}
                    </Alert>
                )}

                <Box
                    component="form"
                    onSubmit={handleSubmit}
                >

                    <TextField
                        fullWidth
                        label="First name"
                        margin="normal"
                        value={firstName}
                        onChange={(e) => setFirstName(e.target.value)}
                    />

                    <TextField
                        fullWidth
                        label="Last name"
                        margin="normal"
                        value={lastName}
                        onChange={(e) => setLastName(e.target.value)}
                    />

                    <TextField
                        fullWidth
                        label="Email"
                        type="email"
                        margin="normal"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                    />

                    <TextField
                        fullWidth
                        label="Password"
                        type="password"
                        margin="normal"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />

                    <Button
                        type="submit"
                        fullWidth
                        variant="contained"
                        sx={{
                            mt: 3,
                            mb: 2,
                        }}
                    >
                        Register
                    </Button>

                    <Typography align="center">

                        Already have an account ?

                        {" "}

                        <Link to="/login">
                            Login
                        </Link>

                    </Typography>

                </Box>

            </Paper>

        </Box>

    );

}