import { useState, type FormEvent } from "react";

import { TextField } from "../forms/TextField";
import type { BacklogCreatePayload } from "../../types";

const GRADES = ["E", "F", "X"];

interface BacklogFormProps {
  onSubmit: (payload: BacklogCreatePayload) => Promise<void>;
}

export function BacklogForm({ onSubmit }: BacklogFormProps) {
  const [subject, setSubject] = useState("");
  const [courseCode, setCourseCode] = useState("");
  const [credits, setCredits] = useState("4");
  const [courseType, setCourseType] = useState("Core Course");
  const [currentGrade, setCurrentGrade] = useState("F");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setIsSubmitting(true);
    try {
      await onSubmit({
        subject,
        course_code: courseCode,
        credits: Number(credits),
        course_type: courseType,
        current_grade: currentGrade,
      });
      setSubject("");
      setCourseCode("");
      setCredits("4");
      setCourseType("Core Course");
      setCurrentGrade("F");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="card-plate flex flex-col gap-4 p-5">
      <p className="label-tag text-ink/50">Add a pending backlog</p>
      <TextField
        label="Subject"
        required
        placeholder="e.g. Data Structures"
        value={subject}
        onChange={(e) => setSubject(e.target.value)}
      />
      <div className="grid grid-cols-2 gap-3">
        <TextField
          label="Course Code"
          required
          placeholder="e.g. UCS301"
          value={courseCode}
          onChange={(e) => setCourseCode(e.target.value)}
        />
        <TextField
          label="Credits"
          type="number"
          step="0.5"
          min="0.5"
          max="10"
          required
          value={credits}
          onChange={(e) => setCredits(e.target.value)}
        />
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="label-tag mb-1.5 block text-ink">Course Type</label>
          <select
            className="field-input"
            value={courseType}
            onChange={(e) => setCourseType(e.target.value)}
          >
            <option>Core Course</option>
            <option>Prerequisite Course</option>
            <option>Foundation Course</option>
            <option>Professional Elective</option>
          </select>
        </div>
        <div>
          <label className="label-tag mb-1.5 block text-ink">Last Attempted Grade</label>
          <select
            className="field-input"
            value={currentGrade}
            onChange={(e) => setCurrentGrade(e.target.value)}
          >
            {GRADES.map((g) => (
              <option key={g}>{g}</option>
            ))}
          </select>
        </div>
      </div>
      <button type="submit" className="btn-primary" disabled={isSubmitting}>
        {isSubmitting ? "Adding..." : "Add Backlog"}
      </button>
    </form>
  );
}
