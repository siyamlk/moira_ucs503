import { useEffect, useState } from "react";

import { EmptyState } from "../../components/common/EmptyState";
import { ErrorBanner } from "../../components/common/ErrorBanner";
import { LoadingState } from "../../components/common/LoadingState";
import { PlateTag } from "../../components/common/PlateTag";
import { TextField } from "../../components/forms/TextField";
import { getApiErrorMessage } from "../../services/api";
import { adminConfigService } from "../../services/adminConfigService";
import type { AcademicConfig, RecommendationWeights } from "../../types/admin";

const WEIGHT_KEYS: (keyof RecommendationWeights)[] = [
  "interest",
  "career",
  "syllabus",
  "skill",
  "academic",
  "prerequisite",
];

function isRecommendationWeights(value: unknown): value is RecommendationWeights {
  return (
    typeof value === "object" &&
    value !== null &&
    WEIGHT_KEYS.every((k) => typeof (value as Record<string, unknown>)[k] === "number")
  );
}

export function AdminConfigPage() {
  const [configs, setConfigs] = useState<AcademicConfig[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [newKey, setNewKey] = useState("");
  const [newValue, setNewValue] = useState("");
  const [newDescription, setNewDescription] = useState("");
  const [newError, setNewError] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);

  async function load() {
    setIsLoading(true);
    setError(null);
    try {
      setConfigs(await adminConfigService.list());
    } catch (err) {
      setError(getApiErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleCreate() {
    setNewError(null);
    let parsed: unknown;
    try {
      parsed = JSON.parse(newValue);
    } catch {
      setNewError("Value must be valid JSON, e.g. a number, string, list, or object.");
      return;
    }
    setIsCreating(true);
    try {
      await adminConfigService.update(newKey.trim(), { value: parsed, description: newDescription });
      setNewKey("");
      setNewValue("");
      setNewDescription("");
      await load();
    } catch (err) {
      setNewError(getApiErrorMessage(err));
    } finally {
      setIsCreating(false);
    }
  }

  return (
    <div className="flex flex-col gap-8">
      <div className="card-plate p-6 sm:p-8">
        <PlateTag>Admin &middot; Rules</PlateTag>
        <h1 className="mt-4 font-serif text-3xl font-bold text-ink">Academic configuration</h1>
        <p className="mt-2 max-w-2xl text-ink/70">
          These values feed directly into the advisory engines — the engines still own how scoring
          and ranking work, this only tunes the numbers they use.
        </p>
      </div>

      {error && <ErrorBanner message={error} />}

      {isLoading ? (
        <LoadingState label="Loading configuration..." />
      ) : configs.length === 0 ? (
        <EmptyState title="No configuration yet" description="Add a key below to get started." />
      ) : (
        <div className="flex flex-col gap-6">
          {configs.map((config) => (
            <ConfigCard key={config.key} config={config} onSaved={load} />
          ))}
        </div>
      )}

      <div className="card-plate p-6 sm:p-8">
        <h2 className="font-serif text-xl font-bold text-ink">Add a configuration key</h2>
        <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
          <TextField label="Key" value={newKey} onChange={(e) => setNewKey(e.target.value)} required />
          <TextField
            label="Description"
            value={newDescription}
            onChange={(e) => setNewDescription(e.target.value)}
          />
        </div>
        <div className="mt-4">
          <label className="label-tag mb-1.5 block text-ink">Value (JSON)</label>
          <textarea
            className="field-input min-h-[80px] resize-y font-mono text-sm"
            placeholder='e.g. ["Elective I", "Elective II"] or {"interest": 25}'
            value={newValue}
            onChange={(e) => setNewValue(e.target.value)}
          />
        </div>
        {newError && (
          <div className="mt-4">
            <ErrorBanner message={newError} />
          </div>
        )}
        <button
          type="button"
          className="btn-primary mt-4"
          onClick={handleCreate}
          disabled={isCreating || !newKey.trim() || !newValue.trim()}
        >
          {isCreating ? "Saving..." : "Save Key"}
        </button>
      </div>
    </div>
  );
}

function ConfigCard({ config, onSaved }: { config: AcademicConfig; onSaved: () => void }) {
  return (
    <div className="card-plate p-6">
      <div className="flex items-baseline justify-between gap-4">
        <h3 className="font-mono text-sm font-bold text-ink">{config.key}</h3>
        <span className="label-tag text-ink/40">
          Updated {new Date(config.updated_at).toLocaleString()}
        </span>
      </div>
      {config.description && <p className="mt-1 text-sm text-ink/60">{config.description}</p>}

      {isRecommendationWeights(config.value) ? (
        <WeightsEditor configKey={config.key} value={config.value} onSaved={onSaved} />
      ) : (
        <JsonEditor configKey={config.key} value={config.value} onSaved={onSaved} />
      )}
    </div>
  );
}

function WeightsEditor({
  configKey,
  value,
  onSaved,
}: {
  configKey: string;
  value: RecommendationWeights;
  onSaved: () => void;
}) {
  const [weights, setWeights] = useState<RecommendationWeights>(value);
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  const sum = WEIGHT_KEYS.reduce((acc, k) => acc + (Number(weights[k]) || 0), 0);
  const isValid = sum === 100;

  async function handleSave() {
    setError(null);
    setIsSaving(true);
    try {
      await adminConfigService.update(configKey, { value: weights });
      onSaved();
    } catch (err) {
      setError(getApiErrorMessage(err));
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <div className="mt-4">
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
        {WEIGHT_KEYS.map((key) => (
          <div key={key}>
            <label className="label-tag mb-1 block text-ink/60">{key}</label>
            <input
              type="number"
              className="field-input"
              value={weights[key]}
              onChange={(e) => setWeights({ ...weights, [key]: Number(e.target.value) })}
            />
          </div>
        ))}
      </div>
      <p className={`label-tag mt-2 ${isValid ? "text-moss" : "text-clay"}`}>
        Sum: {sum} / 100 {isValid ? "✓" : "— must equal 100"}
      </p>
      {error && (
        <div className="mt-2">
          <ErrorBanner message={error} />
        </div>
      )}
      <button type="button" className="btn-primary mt-3" onClick={handleSave} disabled={!isValid || isSaving}>
        {isSaving ? "Saving..." : "Save Weights"}
      </button>
    </div>
  );
}

function JsonEditor({ configKey, value, onSaved }: { configKey: string; value: unknown; onSaved: () => void }) {
  const [text, setText] = useState(JSON.stringify(value, null, 2));
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  async function handleSave() {
    setError(null);
    let parsed: unknown;
    try {
      parsed = JSON.parse(text);
    } catch {
      setError("Value must be valid JSON.");
      return;
    }
    setIsSaving(true);
    try {
      await adminConfigService.update(configKey, { value: parsed });
      onSaved();
    } catch (err) {
      setError(getApiErrorMessage(err));
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <div className="mt-4">
      <textarea
        className="field-input min-h-[90px] resize-y font-mono text-sm"
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      {error && (
        <div className="mt-2">
          <ErrorBanner message={error} />
        </div>
      )}
      <button type="button" className="btn-primary mt-3" onClick={handleSave} disabled={isSaving}>
        {isSaving ? "Saving..." : "Save"}
      </button>
    </div>
  );
}
