import {
  type FormEvent,
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";
import {
  CalendarDays,
  Loader2,
  Pencil,
  Plus,
  RefreshCw,
  Trash2,
  User,
} from "lucide-react";
import { useInterviewNotes } from "../../hooks/useInterviewNotes";
import type {
  InterviewNoteResponse,
  InterviewNoteUpdatePayload,
} from "../../lib/api";
import {
  Alert,
  AlertDescription,
} from "../ui/alert";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "../ui/alert-dialog";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Textarea } from "../ui/textarea";

const MAX_NAME_LENGTH = 255;
const MAX_PROFILE_LENGTH = 500;
const MAX_NOTES_LENGTH = 10_000;

interface NoteDraft {
  intervieweeName: string;
  intervieweeProfile: string;
  notes: string;
  interviewedAt: string;
}

interface DeleteFocusPlan {
  noteId: number;
  nextNoteId: number | null;
  previousNoteId: number | null;
}

type NoteDraftField = keyof NoteDraft;
type InterviewNotesHook = ReturnType<typeof useInterviewNotes>;

function toDateTimeLocal(value: string | null): string {
  if (!value) {
    return "";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "";
  }

  const localDate = new Date(date.getTime() - date.getTimezoneOffset() * 60_000);
  return localDate.toISOString().slice(0, 16);
}

function toApiDateTime(value: string): string | null {
  return value ? new Date(value).toISOString() : null;
}

function formatInterviewDate(value: string | null): string | null {
  if (!value) {
    return null;
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return null;
  }

  return date.toLocaleString("tr-TR", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function noteToDraft(note: InterviewNoteResponse): NoteDraft {
  return {
    intervieweeName: note.interviewee_name,
    intervieweeProfile: note.interviewee_profile,
    notes: note.notes,
    interviewedAt: toDateTimeLocal(note.interviewed_at),
  };
}

function validateDraft(draft: NoteDraft): string | null {
  if (!draft.notes.trim()) {
    return "Görüşme notu boş bırakılamaz.";
  }
  if (draft.intervieweeName.trim().length > MAX_NAME_LENGTH) {
    return `Görüşülen kişi en fazla ${MAX_NAME_LENGTH} karakter olabilir.`;
  }
  if (draft.intervieweeProfile.trim().length > MAX_PROFILE_LENGTH) {
    return `Profil en fazla ${MAX_PROFILE_LENGTH} karakter olabilir.`;
  }
  if (draft.notes.trim().length > MAX_NOTES_LENGTH) {
    return `Görüşme notu en fazla ${MAX_NOTES_LENGTH} karakter olabilir.`;
  }
  if (
    draft.interviewedAt &&
    Number.isNaN(new Date(draft.interviewedAt).getTime())
  ) {
    return "Görüşme tarihi geçerli olmalı.";
  }

  return null;
}

function withoutDraft(
  drafts: Record<number, NoteDraft>,
  noteId: number,
): Record<number, NoteDraft> {
  const nextDrafts = { ...drafts };
  delete nextDrafts[noteId];
  return nextDrafts;
}

function withoutValidationError(
  errors: Record<number, string>,
  noteId: number,
): Record<number, string> {
  const nextErrors = { ...errors };
  delete nextErrors[noteId];
  return nextErrors;
}

function onlyExistingNotes<T>(
  values: Record<number, T>,
  existingNoteIds: Set<number>,
): Record<number, T> {
  const entries = Object.entries(values).filter(([noteId]) =>
    existingNoteIds.has(Number(noteId)),
  );
  return entries.length === Object.keys(values).length
    ? values
    : Object.fromEntries(entries);
}

export function InterviewNotesBody({
  ideaId,
  refreshToken,
}: {
  ideaId: number;
  refreshToken: number;
}) {
  const interviewNotes = useInterviewNotes(ideaId, refreshToken);
  return (
    <InterviewNotesContent
      key={ideaId}
      interviewNotes={interviewNotes}
    />
  );
}

function InterviewNotesContent({
  interviewNotes,
}: {
  interviewNotes: InterviewNotesHook;
}) {
  const {
    status,
    notes,
    loadError,
    reload,
    addNote,
    updateNote,
    deleteNote,
    isCreating,
    createError,
    updatingNoteIds,
    updateErrors,
    deletingNoteIds,
    deleteErrors,
    clearCreateError,
    clearUpdateError,
    clearDeleteError,
  } = interviewNotes;
  const [showForm, setShowForm] = useState(false);
  const [createDraft, setCreateDraft] = useState<NoteDraft>({
    intervieweeName: "",
    intervieweeProfile: "",
    notes: "",
    interviewedAt: "",
  });
  const [createValidationError, setCreateValidationError] = useState<string | null>(
    null,
  );
  const [editDrafts, setEditDrafts] = useState<Record<number, NoteDraft>>({});
  const [editSnapshots, setEditSnapshots] = useState<
    Record<number, NoteDraft>
  >({});
  const [editValidationErrors, setEditValidationErrors] = useState<
    Record<number, string>
  >({});
  const [deleteDialogNoteId, setDeleteDialogNoteId] = useState<number | null>(
    null,
  );
  const rootRef = useRef<HTMLDivElement>(null);
  const focusFrameRef = useRef<number | null>(null);
  const deleteFocusPlanRef = useRef<DeleteFocusPlan | null>(null);

  const scheduleFocus = useCallback((selectors: string[]) => {
    if (focusFrameRef.current !== null) {
      cancelAnimationFrame(focusFrameRef.current);
    }

    focusFrameRef.current = requestAnimationFrame(() => {
      focusFrameRef.current = null;
      for (const selector of selectors) {
        const target = rootRef.current?.querySelector<HTMLElement>(selector);
        if (target) {
          target.focus();
          return;
        }
      }
    });
  }, []);

  const focusCreateTrigger = useCallback(() => {
    scheduleFocus([
      "[data-interview-note-create-trigger]:not(:disabled)",
      "[data-interview-note-create-input]:not(:disabled)",
    ]);
  }, [scheduleFocus]);

  const focusEditTrigger = useCallback(
    (noteId: number) => {
      scheduleFocus([
        `[data-interview-note-edit-trigger="${noteId}"]:not(:disabled)`,
        "[data-interview-note-create-trigger]:not(:disabled)",
        "[data-interview-note-create-input]:not(:disabled)",
      ]);
    },
    [scheduleFocus],
  );

  const focusAfterDelete = useCallback(
    (plan: DeleteFocusPlan) => {
      const selectors: string[] = [];
      if (plan.nextNoteId !== null) {
        selectors.push(
          `[data-interview-note-card-id="${plan.nextNoteId}"] button:not(:disabled)`,
        );
      }
      if (plan.previousNoteId !== null) {
        selectors.push(
          `[data-interview-note-card-id="${plan.previousNoteId}"] button:not(:disabled)`,
        );
      }
      selectors.push(
        "[data-interview-note-create-trigger]:not(:disabled)",
        "[data-interview-note-create-input]:not(:disabled)",
      );
      scheduleFocus(selectors);
    },
    [scheduleFocus],
  );

  useEffect(
    () => () => {
      if (focusFrameRef.current !== null) {
        cancelAnimationFrame(focusFrameRef.current);
      }
    },
    [],
  );

  useEffect(() => {
    if (status !== "ready") {
      return;
    }

    const existingNoteIds = new Set(notes.map((note) => note.id));
    setEditDrafts((previousDrafts) =>
      onlyExistingNotes(previousDrafts, existingNoteIds),
    );
    setEditSnapshots((previousSnapshots) =>
      onlyExistingNotes(previousSnapshots, existingNoteIds),
    );
    setEditValidationErrors((previousErrors) =>
      onlyExistingNotes(previousErrors, existingNoteIds),
    );

    const focusPlan = deleteFocusPlanRef.current;
    if (focusPlan && !existingNoteIds.has(focusPlan.noteId)) {
      deleteFocusPlanRef.current = null;
      setDeleteDialogNoteId((currentNoteId) =>
        currentNoteId === focusPlan.noteId ? null : currentNoteId,
      );
      focusAfterDelete(focusPlan);
    }
  }, [focusAfterDelete, notes, status]);

  const handleCreateDraftChange = (field: NoteDraftField, value: string) => {
    setCreateDraft((previousDraft) => ({ ...previousDraft, [field]: value }));
    setCreateValidationError(null);
    if (createError) {
      clearCreateError();
    }
  };

  const handleCreateSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setCreateValidationError(null);

    const validationError = validateDraft(createDraft);
    if (validationError) {
      setCreateValidationError(validationError);
      return;
    }

    const created = await addNote({
      interviewee_name: createDraft.intervieweeName.trim(),
      interviewee_profile: createDraft.intervieweeProfile.trim(),
      notes: createDraft.notes.trim(),
      interviewed_at: toApiDateTime(createDraft.interviewedAt),
    });

    if (created) {
      setCreateDraft({
        intervieweeName: "",
        intervieweeProfile: "",
        notes: "",
        interviewedAt: "",
      });
      setShowForm(false);
      focusCreateTrigger();
    }
  };

  const startEditing = (note: InterviewNoteResponse) => {
    const snapshot = noteToDraft(note);
    clearUpdateError(note.id);
    setEditValidationErrors((previousErrors) =>
      withoutValidationError(previousErrors, note.id),
    );
    setEditSnapshots((previousSnapshots) => ({
      ...previousSnapshots,
      [note.id]: snapshot,
    }));
    setEditDrafts((previousDrafts) => ({
      ...previousDrafts,
      [note.id]: { ...snapshot },
    }));
  };

  const cancelEditing = (noteId: number) => {
    clearUpdateError(noteId);
    setEditDrafts((previousDrafts) => withoutDraft(previousDrafts, noteId));
    setEditSnapshots((previousSnapshots) =>
      withoutDraft(previousSnapshots, noteId),
    );
    setEditValidationErrors((previousErrors) =>
      withoutValidationError(previousErrors, noteId),
    );
    focusEditTrigger(noteId);
  };

  const handleEditDraftChange = (
    noteId: number,
    field: NoteDraftField,
    value: string,
  ) => {
    setEditDrafts((previousDrafts) => {
      const draft = previousDrafts[noteId];
      return draft
        ? {
            ...previousDrafts,
            [noteId]: { ...draft, [field]: value },
          }
        : previousDrafts;
    });
    setEditValidationErrors((previousErrors) =>
      withoutValidationError(previousErrors, noteId),
    );
    if (updateErrors[noteId]) {
      clearUpdateError(noteId);
    }
  };

  const handleUpdateSubmit = async (
    event: FormEvent<HTMLFormElement>,
    noteId: number,
  ) => {
    event.preventDefault();
    const draft = editDrafts[noteId];
    const snapshot = editSnapshots[noteId];
    if (!draft || !snapshot) {
      return;
    }

    const validationError = validateDraft(draft);
    if (validationError) {
      setEditValidationErrors((previousErrors) => ({
        ...previousErrors,
        [noteId]: validationError,
      }));
      return;
    }

    const intervieweeName = draft.intervieweeName.trim();
    const intervieweeProfile = draft.intervieweeProfile.trim();
    const notesText = draft.notes.trim();
    const payload: InterviewNoteUpdatePayload = {};

    if (intervieweeName !== snapshot.intervieweeName.trim()) {
      payload.interviewee_name = intervieweeName;
    }
    if (intervieweeProfile !== snapshot.intervieweeProfile.trim()) {
      payload.interviewee_profile = intervieweeProfile;
    }
    if (notesText !== snapshot.notes.trim()) {
      payload.notes = notesText;
    }
    if (draft.interviewedAt !== snapshot.interviewedAt) {
      payload.interviewed_at = toApiDateTime(draft.interviewedAt);
    }

    if (Object.keys(payload).length === 0) {
      cancelEditing(noteId);
      return;
    }

    const updated = await updateNote(noteId, payload);

    if (updated) {
      setEditDrafts((previousDrafts) => withoutDraft(previousDrafts, noteId));
      setEditSnapshots((previousSnapshots) =>
        withoutDraft(previousSnapshots, noteId),
      );
      setEditValidationErrors((previousErrors) =>
        withoutValidationError(previousErrors, noteId),
      );
      focusEditTrigger(noteId);
    }
  };

  const handleDeleteDialogChange = (noteId: number, open: boolean) => {
    const isDeleting = deletingNoteIds.includes(noteId);
    if (open) {
      clearDeleteError(noteId);
      setDeleteDialogNoteId(noteId);
      return;
    }
    if (isDeleting) {
      return;
    }

    if (deleteFocusPlanRef.current?.noteId === noteId) {
      deleteFocusPlanRef.current = null;
    }
    clearDeleteError(noteId);
    setDeleteDialogNoteId((currentNoteId) =>
      currentNoteId === noteId ? null : currentNoteId,
    );
  };

  const handleDelete = async (noteId: number) => {
    const noteIndex = notes.findIndex((note) => note.id === noteId);
    const focusPlan: DeleteFocusPlan = {
      noteId,
      nextNoteId:
        noteIndex >= 0 ? (notes[noteIndex + 1]?.id ?? null) : null,
      previousNoteId:
        noteIndex > 0 ? (notes[noteIndex - 1]?.id ?? null) : null,
    };
    deleteFocusPlanRef.current = focusPlan;

    const deleted = await deleteNote(noteId);
    if (!deleted) {
      return;
    }

    const shouldRestoreFocus = deleteFocusPlanRef.current === focusPlan;
    if (shouldRestoreFocus) {
      deleteFocusPlanRef.current = null;
    }
    setEditDrafts((previousDrafts) => withoutDraft(previousDrafts, noteId));
    setEditSnapshots((previousSnapshots) =>
      withoutDraft(previousSnapshots, noteId),
    );
    setEditValidationErrors((previousErrors) =>
      withoutValidationError(previousErrors, noteId),
    );
    setDeleteDialogNoteId(null);
    if (shouldRestoreFocus) {
      focusAfterDelete(focusPlan);
    }
  };

  return (
    <div ref={rootRef}>
      {status === "loading" && notes.length === 0 && (
        <div className="space-y-2.5" aria-busy="true" aria-label="Görüşme notları yükleniyor">
          {[0, 1].map((index) => (
            <div
              key={index}
              className="h-12 animate-pulse rounded-xl border border-border bg-muted/40"
            />
          ))}
        </div>
      )}

      {status === "error" && (
        <Alert variant="destructive" className="mb-3" aria-live="assertive">
          <AlertDescription>
            <p>{loadError}</p>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => void reload()}
              className="mt-2 text-xs"
            >
              <RefreshCw aria-hidden="true" />
              Tekrar Dene
            </Button>
          </AlertDescription>
        </Alert>
      )}

      {(status === "ready" || notes.length > 0) && (
        <div
          className="mb-3 space-y-2.5"
          aria-busy={status === "loading"}
        >
          {status === "ready" && notes.length === 0 && (
            <p className="text-sm leading-relaxed text-muted-foreground">
              Henüz görüşme notu eklenmedi. Bir müşteri görüşmesi yaptıktan sonra
              notlarını buraya ekle; AI asistanı bu notları riskli varsayımlarını
              doğrulamak için kullanabilir.
            </p>
          )}

          {notes.map((note) => {
            const editDraft = editDrafts[note.id];
            const isUpdating = updatingNoteIds.includes(note.id);
            const isDeleting = deletingNoteIds.includes(note.id);
            const editError =
              editValidationErrors[note.id] ?? updateErrors[note.id] ?? null;
            const interviewDateLabel = formatInterviewDate(note.interviewed_at);

            return (
              <div
                key={note.id}
                data-interview-note-card-id={note.id}
                className="min-w-0 rounded-xl border border-border bg-secondary p-3.5"
                aria-busy={isUpdating || isDeleting}
              >
                <div className="mb-1.5 flex flex-wrap items-start justify-between gap-2">
                  <div className="min-w-0 flex-1">
                    <div className="flex min-w-0 flex-wrap items-center gap-1.5">
                      <User
                        size={11}
                        className="shrink-0 text-blue-400"
                        aria-hidden="true"
                      />
                      <span className="min-w-0 break-words text-xs font-bold text-foreground">
                        {note.interviewee_name || "İsimsiz görüşme"}
                      </span>
                      {note.interviewee_profile && (
                        <span className="min-w-0 break-words text-[11px] text-muted-foreground">
                          · {note.interviewee_profile}
                        </span>
                      )}
                    </div>
                    {interviewDateLabel && (
                      <div className="mt-1 flex items-center gap-1 text-[11px] text-muted-foreground">
                        <CalendarDays
                          size={11}
                          className="shrink-0"
                          aria-hidden="true"
                        />
                        <span>{interviewDateLabel}</span>
                      </div>
                    )}
                  </div>

                  <div className="flex flex-wrap items-center justify-end gap-1">
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => startEditing(note)}
                      disabled={Boolean(editDraft) || isUpdating || isDeleting}
                      data-interview-note-edit-trigger={note.id}
                      className="text-xs"
                    >
                      <Pencil aria-hidden="true" />
                      Düzenle
                    </Button>

                    <AlertDialog
                      open={deleteDialogNoteId === note.id}
                      onOpenChange={(open) =>
                        handleDeleteDialogChange(note.id, open)
                      }
                    >
                      <AlertDialogTrigger asChild>
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          disabled={isUpdating || isDeleting}
                          className="text-xs text-destructive hover:bg-destructive/10 hover:text-destructive"
                        >
                          {isDeleting ? (
                            <Loader2
                              className="animate-spin"
                              aria-hidden="true"
                            />
                          ) : (
                            <Trash2 aria-hidden="true" />
                          )}
                          Sil
                        </Button>
                      </AlertDialogTrigger>

                      <AlertDialogContent aria-busy={isDeleting}>
                        <AlertDialogHeader>
                          <AlertDialogTitle>
                            Görüşme notunu sil
                          </AlertDialogTitle>
                          <AlertDialogDescription>
                            Bu görüşme notu kalıcı olarak silinecek. Bu işlem geri
                            alınamaz.
                          </AlertDialogDescription>
                        </AlertDialogHeader>

                        {deleteErrors[note.id] && (
                          <Alert
                            variant="destructive"
                            aria-live="assertive"
                          >
                            <AlertDescription>
                              {deleteErrors[note.id]}
                            </AlertDescription>
                          </Alert>
                        )}

                        <AlertDialogFooter>
                          <AlertDialogCancel disabled={isDeleting}>
                            Vazgeç
                          </AlertDialogCancel>
                          <AlertDialogAction
                            disabled={isDeleting}
                            onClick={(event) => {
                              event.preventDefault();
                              void handleDelete(note.id);
                            }}
                            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                          >
                            {isDeleting ? (
                              <>
                                <Loader2
                                  className="animate-spin"
                                  aria-hidden="true"
                                />
                                Siliniyor...
                              </>
                            ) : (
                              "Notu Sil"
                            )}
                          </AlertDialogAction>
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>
                  </div>
                </div>

                {editDraft ? (
                  <form
                    onSubmit={(event) =>
                      void handleUpdateSubmit(event, note.id)
                    }
                    className="mt-3 space-y-3 rounded-xl border border-border bg-muted/40 p-3.5"
                    aria-busy={isUpdating}
                    aria-describedby={
                      editError
                        ? `interview-note-edit-error-${note.id}`
                        : undefined
                    }
                  >
                    <div className="grid min-w-0 grid-cols-1 gap-2 sm:grid-cols-2">
                      <label className="block min-w-0 space-y-1 text-xs font-medium text-foreground">
                        <span className="block">Görüşülen kişi</span>
                        <Input
                          type="text"
                          autoFocus
                          data-interview-note-edit-input={note.id}
                          value={editDraft.intervieweeName}
                          maxLength={MAX_NAME_LENGTH}
                          disabled={isUpdating || isDeleting}
                          onChange={(event) =>
                            handleEditDraftChange(
                              note.id,
                              "intervieweeName",
                              event.target.value,
                            )
                          }
                          className="bg-muted"
                        />
                      </label>

                      <label className="block min-w-0 space-y-1 text-xs font-medium text-foreground">
                        <span className="block">Profil</span>
                        <Input
                          type="text"
                          value={editDraft.intervieweeProfile}
                          maxLength={MAX_PROFILE_LENGTH}
                          disabled={isUpdating || isDeleting}
                          onChange={(event) =>
                            handleEditDraftChange(
                              note.id,
                              "intervieweeProfile",
                              event.target.value,
                            )
                          }
                          className="bg-muted"
                        />
                      </label>

                      <label className="block min-w-0 space-y-1 text-xs font-medium text-foreground sm:col-span-2">
                        <span className="block">Görüşme tarihi</span>
                        <Input
                          type="datetime-local"
                          value={editDraft.interviewedAt}
                          disabled={isUpdating || isDeleting}
                          onChange={(event) =>
                            handleEditDraftChange(
                              note.id,
                              "interviewedAt",
                              event.target.value,
                            )
                          }
                          className="bg-muted"
                        />
                      </label>

                      <label className="block min-w-0 space-y-1 text-xs font-medium text-foreground sm:col-span-2">
                        <span className="block">Görüşme notu</span>
                        <Textarea
                          value={editDraft.notes}
                          maxLength={MAX_NOTES_LENGTH}
                          rows={5}
                          disabled={isUpdating || isDeleting}
                          onChange={(event) =>
                            handleEditDraftChange(
                              note.id,
                              "notes",
                              event.target.value,
                            )
                          }
                          className="min-w-0 bg-muted"
                        />
                      </label>
                    </div>

                    {editError && (
                      <Alert
                        id={`interview-note-edit-error-${note.id}`}
                        variant="destructive"
                        className="py-2 text-xs"
                        aria-live="assertive"
                      >
                        <AlertDescription className="text-xs">
                          {editError}
                        </AlertDescription>
                      </Alert>
                    )}

                    <div className="flex flex-col gap-2 sm:flex-row">
                      <Button
                        type="submit"
                        disabled={isUpdating || isDeleting}
                        className="w-full text-xs sm:w-auto"
                      >
                        {isUpdating ? (
                          <>
                            <Loader2
                              className="animate-spin"
                              aria-hidden="true"
                            />
                            Kaydediliyor...
                          </>
                        ) : (
                          "Değişiklikleri Kaydet"
                        )}
                      </Button>
                      <Button
                        type="button"
                        variant="outline"
                        disabled={isUpdating || isDeleting}
                        onClick={() => cancelEditing(note.id)}
                        className="w-full text-xs sm:w-auto"
                      >
                        İptal
                      </Button>
                    </div>
                  </form>
                ) : (
                  <p className="min-w-0 whitespace-pre-wrap break-words text-xs leading-relaxed text-muted-foreground">
                    {note.notes}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      )}

      {showForm ? (
        <form
          onSubmit={handleCreateSubmit}
          className="space-y-3 rounded-xl border border-border bg-muted/40 p-3.5"
          aria-busy={isCreating}
          aria-describedby={
            createValidationError || createError
              ? "interview-note-create-error"
              : undefined
          }
        >
          <div className="grid min-w-0 grid-cols-1 gap-2 sm:grid-cols-2">
            <label className="block min-w-0 space-y-1 text-xs font-medium text-foreground">
              <span className="block">Görüşülen kişi (opsiyonel)</span>
              <Input
                type="text"
                autoFocus
                data-interview-note-create-input
                value={createDraft.intervieweeName}
                maxLength={MAX_NAME_LENGTH}
                disabled={isCreating}
                onChange={(event) =>
                  handleCreateDraftChange(
                    "intervieweeName",
                    event.target.value,
                  )
                }
                placeholder="Görüşülen kişi"
                className="bg-muted"
              />
            </label>

            <label className="block min-w-0 space-y-1 text-xs font-medium text-foreground">
              <span className="block">Profil (opsiyonel)</span>
              <Input
                type="text"
                value={createDraft.intervieweeProfile}
                maxLength={MAX_PROFILE_LENGTH}
                disabled={isCreating}
                onChange={(event) =>
                  handleCreateDraftChange(
                    "intervieweeProfile",
                    event.target.value,
                  )
                }
                placeholder="Görüşülen kişinin profili"
                className="bg-muted"
              />
            </label>

            <label className="block min-w-0 space-y-1 text-xs font-medium text-foreground sm:col-span-2">
              <span className="block">Görüşme tarihi (opsiyonel)</span>
              <Input
                type="datetime-local"
                value={createDraft.interviewedAt}
                disabled={isCreating}
                onChange={(event) =>
                  handleCreateDraftChange("interviewedAt", event.target.value)
                }
                className="bg-muted"
              />
            </label>

            <label className="block min-w-0 space-y-1 text-xs font-medium text-foreground sm:col-span-2">
              <span className="block">Görüşme notu</span>
              <Textarea
                value={createDraft.notes}
                maxLength={MAX_NOTES_LENGTH}
                rows={4}
                disabled={isCreating}
                onChange={(event) =>
                  handleCreateDraftChange("notes", event.target.value)
                }
                placeholder="Görüşmede konuşulanları özetle..."
                className="min-w-0 bg-muted"
              />
            </label>
          </div>

          {(createValidationError || createError) && (
            <Alert
              id="interview-note-create-error"
              variant="destructive"
              className="py-2 text-xs"
              aria-live="assertive"
            >
              <AlertDescription className="text-xs">
                {createValidationError ?? createError}
              </AlertDescription>
            </Alert>
          )}

          <div className="flex flex-col gap-2 sm:flex-row">
            <Button
              type="submit"
              disabled={isCreating}
              className="w-full text-xs sm:w-auto"
            >
              {isCreating ? (
                <>
                  <Loader2 className="animate-spin" aria-hidden="true" />
                  Kaydediliyor...
                </>
              ) : (
                "Notu Kaydet"
              )}
            </Button>
            <Button
              type="button"
              variant="outline"
              disabled={isCreating}
              onClick={() => {
                setShowForm(false);
                focusCreateTrigger();
              }}
              className="w-full text-xs sm:w-auto"
            >
              Vazgeç
            </Button>
          </div>
        </form>
      ) : (
        <Button
          type="button"
          variant="ghost"
          size="sm"
          data-interview-note-create-trigger
          disabled={isCreating}
          onClick={() => {
            clearCreateError();
            setCreateValidationError(null);
            setShowForm(true);
          }}
          className="text-xs text-primary hover:text-primary"
        >
          <Plus aria-hidden="true" />
          Görüşme Notu Ekle
        </Button>
      )}
    </div>
  );
}
