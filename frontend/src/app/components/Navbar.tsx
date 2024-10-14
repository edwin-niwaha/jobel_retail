import React, { useState } from 'react';
import Link from 'next/link';
import { Navbar, Nav, Container, Button } from 'react-bootstrap';

const NavBar: React.FC = () => {
    const [isLoggedIn, setIsLoggedIn] = useState(false); // Track login state

    const handleLoginLogout = () => {
        setIsLoggedIn(!isLoggedIn); // Toggle login state
    };

    return (
        <Navbar bg="light" expand="lg">
            <Container>
                <Navbar.Brand href="/">Retail Manager</Navbar.Brand>
                <Navbar.Toggle aria-controls="basic-navbar-nav" />
                <Navbar.Collapse id="basic-navbar-nav">
                    <Nav className="ml-auto">
                        <Link href="/" passHref>
                            <Nav.Link as="div">Home</Nav.Link>
                        </Link>
                        <Link href="/about" passHref>
                            <Nav.Link as="div">About</Nav.Link>
                        </Link>
                        <Link href="/contact" passHref>
                            <Nav.Link as="div">Contact</Nav.Link>
                        </Link>

                        {/* Conditional rendering of login/logout button */}
                        {isLoggedIn ? (
                            <Button variant="outline-danger" onClick={handleLoginLogout}>
                                Logout
                            </Button>
                        ) : (
                            <Button variant="outline-primary" onClick={handleLoginLogout}>
                                Login
                            </Button>
                        )}
                    </Nav>
                </Navbar.Collapse>
            </Container>
        </Navbar>
    );
};

export default NavBar;
