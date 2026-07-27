import { type FormEvent, useState } from "react";
import { Plus, RefreshCw, User } from "lucide-react";
import { useInterviewNotes } from "../../hooks/useInterviewNotes";

export function InterviewNotesBody({ ideaId }: { ideaId: number }) {
  const { status, notes, error, reload, addNote, isSubmitting } = useInterviewNotes(ideaId);
  const [showForm, setShowForm] = useState(false);
  const [intervieweeName, setIntervieweeName] = useState("");
  const [intervieweeProfile, setIntervieweeProfile] = useState("");
  const [notesText, setNotesText] = useState("");
  const [formError, setFormError] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setFormError(null);

    if (notesText.trim().length < 10) {
      setFormError("Görüşme notu en az 10 karakter olmalı.");
      return;
    }

    const ok = await addNote({
      interviewee_name: intervieweeName.trim(),
      interviewee_profile: intervieweeProfile.trim(),
      notes: notesText.trim(),
    });

    if (ok) {
      setIntervieweeName("");
      setIntervieweeProfile("");
      setNotesText("");
      setShowForm(false);
    }
  };

  return (
    <div>
      {status === "loading" && (
        <div className="space-y-2.5">
          {[0, 1].map((i) => (
            <div key={i} className="h-12 rounded-xl bg-muted/40 border border-border animate-pulse" />
          ))}
        </div>
      )}

      {status === "error" && (
        <div className="bg-red-900/10 border border-red-800/30 rounded-xl p-4 mb-3">
          <p className="text-xs text-red-400 mb-2.5">{error}</p>
          <button
            onClick={reload}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border border-red-800/40 text-red-400 hover:bg-red-900/20 transition-all"
          >
            <RefreshCw size={12} />Tekrar Dene
          </button>
        </div>
      )}

      {status === "ready" && (
        <div className="space-y-2.5 mb-3">
          {notes.length === 0 && (
            <p className="text-sm text-muted-foreground leading-relaxed">
              Henüz görüşme notu eklenmedi. Bir müşteri görüşmesi yaptıktan sonra notlarını buraya ekle;
              AI asistanı bu notları riskli varsayımlarını doğrulamak için kullanabilir.
            </p>
          )}
          {notes.map((note) => (
            <div key={note.id} className="bg-secondary border border-border rounded-xl p-3.5">
              <div className="flex items-center gap-1.5 mb-1.5">
                <User size={11} className="text-blue-400" />
                <span className="text-xs font-bold text-foreground">
                  {note.interviewee_name || "İsimsiz görüşme"}
                </span>
                {note.interviewee_profile && (
                  <span className="text-[11px] text-muted-foreground">· {note.interviewee_profile}</span>
                )}
              </div>
              <p className="text-xs text-muted-foreground leading-relaxed whitespace-pre-line line-clamp-4">
                {note.notes}
              </p>
            </div>
          ))}
        </div>
      )}

      {showForm ? (
        <form onSubmit={handleSubmit} className="bg-muted/40 border border-border rounded-xl p-3.5 space-y-2.5">
          <div className="grid grid-cols-2 gap-2">
            <input
              type="text"
              value={intervieweeName}
              onChange={(e) => setIntervieweeName(e.target.value)}
              placeholder="Görüşülen kişi (opsiyonel)"
              className="bg-muted border border-border rounded-lg px-2.5 py-2 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary/50"
            />
            <input
              type="text"
              value={intervieweeProfile}
              onChange={(e) => setIntervieweeProfile(e.target.value)}
              placeholder="Profili (opsiyonel)"
              className="bg-muted border border-border rounded-lg px-2.5 py-2 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary/50"
            />
          </div>
          <textarea
            value={notesText}
            onChange={(e) => setNotesText(e.target.value)}
            placeholder="Görüşmede konuşulanları özetle..."
            rows={4}
            className="w-full bg-muted border border-border rounded-lg px-2.5 py-2 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary/50 resize-none"
          />
          {formError && <p className="text-xs text-red-400">{formError}</p>}
          <div className="flex items-center gap-2">
            <button
              type="submit"
              disabled={isSubmitting}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-xs font-semibold bg-primary text-white hover:bg-blue-600 transition-all disabled:opacity-50"
            >
              {isSubmitting ? "Kaydediliyor..." : "Notu Kaydet"}
            </button>
            <button
              type="button"
              onClick={() => setShowForm(false)}
              className="text-xs font-semibold text-muted-foreground hover:text-foreground transition-colors"
            >
              Vazgeç
            </button>
          </div>
        </form>
      ) : (
        <button
          onClick={() => setShowForm(true)}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-blue-400 hover:text-blue-300 transition-colors"
        >
          <Plus size={13} />Görüşme Notu Ekle
        </button>
      )}
    </div>
  );
}
