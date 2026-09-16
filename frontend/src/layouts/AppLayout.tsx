import { Outlet } from "react-router-dom";

import { Footer } from "../components/layout/Footer";
import { Navbar } from "../components/layout/Navbar";

export function AppLayout() {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <main className="mx-auto w-full max-w-7xl flex-1 px-6 py-10">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
