import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";

import { ErrorBanner } from "../../components/common/ErrorBanner";
import { TextField } from "../../components/forms/TextField";
import { useAuth } from "../../context/AuthContext";
import { AuthLayout } from "../../layouts/AuthLayout";
import { getApiErrorMessage } from "../../services/api";

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await login({ email, password });
      navigate("/dashboard");
    } catch (err) {
      setError(getApiErrorMessage(err));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <AuthLayout eyebrow="Scholar Gateway" formTitle="Welcome back.">
      <p className="mb-6 text-sm text-ink/60">Your academic map is waiting.</p>

      <form onSubmit={handleSubmit} className="flex flex-1 flex-col gap-5">
        {error && <ErrorBanner message={error} />}

        <TextField
          label="Email or Student ID"
          type="email"
          required
          placeholder="e.g. abc_be24@thapar.edu"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <div>
          <div className="mb-1.5 flex items-baseline justify-between">
            <label htmlFor="password" className="label-tag text-ink">
              Password
            </label>
            <span className="label-tag cursor-default text-ink/40">Forgot password?</span>
          </div>
          <div className="relative">
            <input
              id="password"
              type={showPassword ? "text" : "password"}
              required
              placeholder="Enter your password"
              className="field-input pr-12"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <button
              type="button"
              onClick={() => setShowPassword((v) => !v)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-xs font-bold text-ink/50 hover:text-ink"
            >
              {showPassword ? "HIDE" : "SHOW"}
            </button>
          </div>
        </div>

        <button type="submit" className="btn-primary mt-2" disabled={isSubmitting}>
          {isSubmitting ? "Entering..." : "Enter MOIRA →"}
        </button>

        <p className="text-center text-xs text-ink/40">
          Demo login: alex.chen@thapar.edu / Demo@1234
        </p>
        <p className="text-center text-xs text-ink/40">
          Admin login: admin@moira.app / AdminPass123!
        </p>

        <div className="mt-auto flex items-center justify-between border-t-2 border-ink pt-4 text-sm">
          <span className="text-ink/60">Don&apos;t have an account?</span>
          <Link to="/signup" className="label-tag text-ink hover:underline">
            Create your map now →
          </Link>
        </div>
      </form>
    </AuthLayout>
  );
}
