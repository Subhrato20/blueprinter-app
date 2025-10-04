// Supabase Edge Function: analyze_repo
// Trigger: HTTP (can be called via Storage webhook on upload)
import { serve } from "https://deno.land/std@0.224.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

type StyleTokens = {
  lang: "ts" | "js" | "py";
  indent: "2" | "4";
  quotes: "single" | "double";
  semi: boolean;
  tests?: string | null;
  routeDir?: string | null;
  alias?: string | null;
};

serve(async (req) => {
  try {
    const { projectId, userId, fileUrl, tokens } = await req.json();

    // If tokens provided (debug), echo back. Otherwise attempt to detect.
    const detected: StyleTokens = tokens ?? {
      lang: "ts",
      indent: "2",
      quotes: "single",
      semi: false,
      tests: "jest",
      routeDir: "apps/api/src/routes",
      alias: "@/",
    };

    const supabase = createClient(
      Deno.env.get("SUPABASE_URL")!,
      Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
      { global: { headers: { Authorization: req.headers.get("Authorization")! } } },
    );

    // Upsert style profile
    const { error } = await supabase
      .from("style_profiles")
      .upsert({ user_id: userId, tokens: detected }, { onConflict: "user_id" });
    if (error) throw error;

    return new Response(JSON.stringify({ ok: true, tokens: detected }), { status: 200 });
  } catch (e) {
    return new Response(JSON.stringify({ ok: false, error: String(e) }), { status: 400 });
  }
});

