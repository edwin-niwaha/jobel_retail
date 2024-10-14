"use client";

import useSWR from "swr";
import { fetcher } from "@/app/fetcher";
import NavBar from "@/app/components/Navbar"; // Import your NavBar
import { AuthActions } from "@/app/utils/auth";
import { useRouter } from "next/navigation";
import { Container } from "react-bootstrap"; //

export default function Home() {
  const router = useRouter();
  const { data: user } = useSWR("/api/auth/users/me", fetcher);
  const { logout, removeTokens } = AuthActions();

  const handleLogout = () => {
    logout()
      .res(() => {
        removeTokens();
        router.push("/");
      })
      .catch(() => {
        removeTokens();
        router.push("/");
      });
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      {/* Include the NavBar */}
      <NavBar />

      {/* Use Container for fluid layout */}
      <Container fluid className="flex-grow p-6">
        <h1 className="text-3xl font-bold mb-6">Dashboard</h1>

        {/* Dashboard Cards Container */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* User Card */}
          <div className="bg-white p-6 rounded-lg shadow-lg">
            <h2 className="text-xl font-semibold mb-2">Hello, {user?.username}!</h2>
            <p className="mb-4">Your account details:</p>
            <ul>
              <li>Username: {user?.username}</li>
              <li>Email: {user?.email}</li>
            </ul>
            <button
              onClick={handleLogout}
              className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-700 transition-colors mt-4"
            >
              Disconnect
            </button>
          </div>

          {/* Stats Card 1 */}
          <div className="bg-blue-500 text-white p-6 rounded-lg shadow-lg">
            <h2 className="text-xl font-semibold">Total Sales</h2>
            <p className="text-3xl font-bold">120</p>
            <p className="mt-2">This Month</p>
          </div>

          {/* Stats Card 2 */}
          <div className="bg-green-500 text-white p-6 rounded-lg shadow-lg">
            <h2 className="text-xl font-semibold">New Users</h2>
            <p className="text-3xl font-bold">45</p>
            <p className="mt-2">This Month</p>
          </div>

          {/* Stats Card 3 */}
          <div className="bg-orange-500 text-white p-6 rounded-lg shadow-lg">
            <h2 className="text-xl font-semibold">Pending Orders</h2>
            <p className="text-3xl font-bold">7</p>
            <p className="mt-2">To Fulfill</p>
          </div>

          {/* More cards can be added here */}
        </div>
      </Container>
    </div>
  );
}