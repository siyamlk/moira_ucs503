import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";

import { ErrorBanner } from "../../components/common/ErrorBanner";
import { TextField } from "../../components/forms/TextField";
import { useAuth } from "../../context/AuthContext";
import { AuthLayout } from "../../layouts/AuthLayout";
import { getApiErrorMessage } from "../../services/api";

export function SignupPage() {
  const { signup } = useAuth();
  const navigate = useNavigate();
  const [fullName, setFullName] = useState("");
  const [studentId, setStudentId] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }
    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }

    setIsSubmitting(true);
    try {
      await signup({ full_name: fullName, student_id: studentId, email, password });
      navigate("/dashboard");
    } catch (err) {
      setError(getApiErrorMessage(err));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <AuthLayout eyebrow="Scholar Gateway · Entrance" formTitle="Begin your map.">
      <p className="mb-6 text-sm text-ink/60">Create your student account and start your academic journey.</p>

      <form onSubmit={handleSubmit} className="flex flex-1 flex-col gap-5">
        {error && <ErrorBanner message={error} />}

        <TextField
          label="Full Name"
          required
          placeholder="Enter your full name"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
        />

        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
          <TextField
            label="Student ID"
            required
            placeholder="Enter your student ID"
            value={studentId}
            onChange={(e) => setStudentId(e.target.value)}
          />
          <TextField
            label="University Email"
            type="email"
            required
            placeholder="Enter your university email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>

        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
          <TextField
            label="Password"
            type="password"
            required
            placeholder="Create a password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <TextField
            label="Confirm Password"
            type="password"
            required
            placeholder="Confirm your password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
          />
        </div>

        <div className="border-2 border-ink bg-parchmentDark px-4 py-3 text-sm text-ink/70">
          <strong className="text-ink">Note:</strong> Your academic profile, interests, and
          backlogs will be set up in My Moira once inside.
        </div>

        <button type="submit" className="btn-primary mt-2" disabled={isSubmitting}>
          {isSubmitting ? "Creating..." : "Create My Moira →"}
        </button>

        <div className="mt-auto flex items-center justify-between border-t-2 border-ink pt-4 text-sm">
          <span className="text-ink/60">Already have an account?</span>
          <Link to="/login" className="label-tag text-ink hover:underline">
            Log in →
          </Link>
        </div>
      </form>
    </AuthLayout>
  );
}
