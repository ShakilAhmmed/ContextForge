import { MessageSquare, Send, User as UserIcon } from "lucide-react";
import { type FormEvent, useState } from "react";
import { Link } from "react-router-dom";

import { useAskQuestionMutation } from "../../api/chatApi";
import { reportError } from "../../api/errors";
import type { ChatResponse } from "../../api/types";
import { AppLayout } from "../../components/AppLayout";
import { PageHeader } from "../../components/PageHeader";
import { SubmitButton } from "../../components/SubmitButton";

interface Exchange {
  question: string;
  response: ChatResponse;
}

export function ChatPage() {
  const [question, setQuestion] = useState("");
  const [history, setHistory] = useState<Exchange[]>([]);
  const [askQuestion, { isLoading }] = useAskQuestionMutation();

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const asked = question.trim();
    if (!asked) return;

    try {
      const response = await askQuestion({ question: asked }).unwrap();
      setHistory((prev) => [...prev, { question: asked, response }]);
      setQuestion("");
    } catch (err) {
      reportError(err);
    }
  }

  return (
    <AppLayout>
      <PageHeader
        icon={MessageSquare}
        title="Chat"
        description="Ask a question about your uploaded documents."
      />

      <div className="mb-4 space-y-4">
        {history.length === 0 && (
          <div className="rounded-xl bg-white p-10 text-center text-sm text-slate-500 shadow-sm ring-1 ring-slate-200">
            No questions asked yet - try asking something about a document you've uploaded.
          </div>
        )}

        {history.map((exchange, index) => (
          <div key={index} className="animate-fade-in-up space-y-3">
            <div className="flex items-start gap-3">
              <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-slate-200 text-slate-600">
                <UserIcon className="size-4" />
              </div>
              <div className="rounded-xl bg-white px-4 py-2.5 text-sm text-slate-800 shadow-sm ring-1 ring-slate-200">
                {exchange.question}
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-violet-600 text-white">
                <MessageSquare className="size-4" />
              </div>
              <div className="flex-1 space-y-2">
                <div className="whitespace-pre-wrap rounded-xl bg-indigo-50 px-4 py-2.5 text-sm text-slate-800">
                  {exchange.response.answer}
                </div>
                {exchange.response.citations.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {exchange.response.citations.map((citation, citationIndex) => (
                      <Link
                        key={citationIndex}
                        to={`/documents/${citation.document_id}`}
                        className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600 transition-colors hover:bg-slate-200"
                      >
                        {citation.filename}
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      <form
        onSubmit={handleSubmit}
        className="sticky bottom-6 flex gap-2 rounded-xl bg-white p-3 shadow-lg ring-1 ring-slate-200"
      >
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question about your documents..."
          className="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
        />
        <SubmitButton loading={isLoading} className="w-auto px-4">
          <span className="flex items-center gap-1.5">
            <Send className="size-4" />
            Ask
          </span>
        </SubmitButton>
      </form>
    </AppLayout>
  );
}
