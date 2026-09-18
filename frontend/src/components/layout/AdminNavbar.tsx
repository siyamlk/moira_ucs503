import { NavLink, useNavigate } from "react-router-dom";

import { useAuth } from "../../context/AuthContext";
import { initials } from "../../utils/format";

const LINKS = [
  { to: "/admin", label: "Dashboard", end: true },
  { to: "/admin/electives", label: "Courses & Electives" },
  { to: "/admin/faculty", label: "Faculty" },
  { to: "/admin/schedules", label: "Schedules" },
  { to: "/admin/bookings", label: "Bookings" },
  { to: "/admin/config", label: "Rules" },
];

export function AdminNavbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <header className="sticky top-0 z-20 border-b-2 border-ink bg-parchment/95 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-6 px-6 py-4">
        <NavLink to="/admin" className="flex items-center gap-3">
          <span className="flex h-9 w-9 items-center justify-center border-2 border-ink bg-clay font-serif text-lg font-bold text-parchment">
            M
          </span>
          <span>
            <span className="block font-serif text-lg font-bold leading-none text-ink">MOIRA Admin</span>
            <span className="label-tag block leading-none text-ink/50">Academic Data Console</span>
          </span>
        </NavLink>

        <nav className="hidden items-center gap-1 md:flex">
          {LINKS.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.end}
              className={({ isActive }) =>
                `label-tag border-2 px-3 py-2 transition-colors ${
                  isActive ? "border-ink bg-ink text-parchment" : "border-transparent text-ink/70 hover:border-ink"
                }`
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>

        <div className="flex items-center gap-3">
          <NavLink to="/dashboard" className="label-tag border-2 border-ink/30 px-2 py-1.5 text-ink/60 hover:border-ink hover:text-ink">
            Student View
          </NavLink>
          {user && (
            <div className="hidden text-right sm:block">
              <p className="label-tag leading-none text-ink/50">Admin</p>
              <p className="font-mono text-xs font-bold leading-tight text-ink">{user.student_id}</p>
            </div>
          )}
          <span
            title={user?.full_name}
            className="flex h-9 w-9 items-center justify-center border-2 border-ink bg-parchmentDark font-mono text-xs font-bold text-ink"
          >
            {user ? initials(user.full_name) : "?"}
          </span>
          <button
            type="button"
            onClick={handleLogout}
            className="label-tag border-2 border-ink/30 px-2 py-1.5 text-ink/60 hover:border-ink hover:text-ink"
            title="Log out"
          >
            Logout
          </button>
        </div>
      </div>
      <nav className="flex items-center gap-1 overflow-x-auto border-t border-ink/20 px-6 py-2 md:hidden">
        {LINKS.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.end}
            className={({ isActive }) =>
              `label-tag whitespace-nowrap border-2 px-3 py-1.5 ${
                isActive ? "border-ink bg-ink text-parchment" : "border-ink/30 text-ink/70"
              }`
            }
          >
            {link.label}
          </NavLink>
        ))}
      </nav>
    </header>
  );
}
