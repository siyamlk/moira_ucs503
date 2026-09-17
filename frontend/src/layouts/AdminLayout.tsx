import { Outlet } from "react-router-dom";

import { AdminNavbar } from "../components/layout/AdminNavbar";
import { Footer } from "../components/layout/Footer";

export function AdminLayout() {
  return (
    <div className="flex min-h-screen flex-col">
      <AdminNavbar />
      <main className="mx-auto w-full max-w-7xl flex-1 px-6 py-10">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
