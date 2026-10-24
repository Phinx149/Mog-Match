import { ExternalLink, FolderGit2 } from "lucide-react";
import type { Project } from "../../types/profile";
import SkillBadge from "./SkillBadge";

export default function ProjectCard({ project }: { project: Project }) {
  return (
    <article className="rounded-xl border border-line bg-surface-raised p-4 transition-colors hover:border-violet-500/40">
      <div className="flex items-start justify-between gap-3">
        <h3 className="flex items-center gap-2 font-semibold text-slate-100">
          <FolderGit2 className="size-4 text-violet-400" aria-hidden />
          {project.title}
        </h3>
        {project.project_url && (
          <a
            href={project.project_url}
            target="_blank"
            rel="noreferrer"
            className="text-muted transition-colors hover:text-cyan-300"
            aria-label={`Open ${project.title}`}
          >
            <ExternalLink className="size-4" aria-hidden />
          </a>
        )}
      </div>
      {project.description && <p className="mt-2 text-sm text-slate-300">{project.description}</p>}
      {project.technologies.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {project.technologies.map((tech) => (
            <SkillBadge key={tech} label={tech} variant="neutral" />
          ))}
        </div>
      )}
    </article>
  );
}
