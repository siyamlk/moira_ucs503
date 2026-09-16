import { NavLink } from "react-router-dom";

import { CampusIllustration } from "../components/common/CampusIllustration";

interface AuthLayoutProps {
  children: React.ReactNode;
  eyebrow: string;
  formTitle: string;
}

export function AuthLayout({ children, eyebrow, formTitle }: AuthLayoutProps) {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="border-b-2 border-ink px-6 py-4">
        <div className="mx-auto flex max-w-6xl items-center justify-between">
          <NavLink to="/" className="flex items-center gap-3">
            <span className="flex h-9 w-9 items-center justify-center border-2 border-ink bg-ink font-serif text-lg font-bold text-parchment">
              M
            </span>
            <span>
              <span className="block font-serif text-lg font-bold leading-none text-ink">MOIRA</span>
              <span className="block font-hand text-sm leading-none text-ink/60">Find your way forward.</span>
            </span>
          </NavLink>
          <span className="label-tag hidden sm:block">Academic Advisory Platform</span>
        </div>
      </header>

      <main className="mx-auto grid w-full max-w-6xl flex-1 grid-cols-1 gap-8 px-6 py-10 lg:grid-cols-2">
        <section className="card-plate flex flex-col justify-between gap-6 p-8">
          <div>
            <p className="label-tag mb-4">{eyebrow}</p>
            <h1 className="font-serif text-4xl font-bold leading-tight text-ink">
              Every choice draws a path.
            </h1>
            <p className="mt-4 text-ink/70">
              Your university life is full of choices — electives, courses, faculty and
              academic decisions. MOIRA helps you make sense of them and find a path that
              fits you.
            </p>
          </div>

          <div className="border-2 border-ink bg-parchmentDark p-4">
            <div className="h-48">
              <CampusIllustration />
            </div>
            <p className="mt-3 font-hand text-lg text-ink/80">
              You are here. Let's start mapping your path.
            </p>
          </div>

          <p className="label-tag text-ink/40">&#9675; Verified Academic Dispatch</p>
        </section>

        <section className="card-plate flex flex-col p-8">
          <div className="mb-6 flex items-center justify-between border-b-2 border-ink pb-4">
            <div>
              <span className="label-tag mb-1 inline-block bg-parchmentDark px-2 py-1">
                Scholar Account
              </span>
              <h2 className="mt-2 font-serif text-2xl font-bold text-ink">{formTitle}</h2>
            </div>
          </div>
          {children}
        </section>
      </main>
    </div>
  );
}
