/**
 * Supabase Edge Function: analyze_repo
 * 
 * Analyzes a repository to extract coding style tokens and create/update
 * a user's style profile in the database.
 */

import { serve } from "https://deno.land/std@0.208.0/http/server.ts";
import { createClient } from "supabase";

interface StyleTokens {
  quotes: "single" | "double";
  semicolons: boolean;
  indent: "spaces" | "tabs";
  indent_size: number;
  test_framework: string;
  directories: string[];
  aliases: Record<string, string>;
  language: "typescript" | "javascript";
}

interface RepoAnalysisRequest {
  repo_url: string;
  user_id: string;
  sample_files?: string[];
}

interface RepoAnalysisResponse {
  success: boolean;
  style_tokens?: StyleTokens;
  error?: string;
}

// Initialize Supabase client
const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
const supabaseServiceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const supabase = createClient(supabaseUrl, supabaseServiceKey);

/**
 * Analyze code style from file content
 */
function analyzeCodeStyle(content: string): Partial<StyleTokens> {
  const tokens: Partial<StyleTokens> = {};
  
  // Analyze quotes
  const singleQuotes = (content.match(/'/g) || []).length;
  const doubleQuotes = (content.match(/"/g) || []).length;
  tokens.quotes = singleQuotes > doubleQuotes ? "single" : "double";
  
  // Analyze semicolons
  const semicolonLines = content.split('\n').filter(line => 
    line.trim().endsWith(';') && !line.trim().startsWith('//')
  ).length;
  const totalLines = content.split('\n').length;
  tokens.semicolons = semicolonLines / totalLines > 0.5;
  
  // Analyze indentation
  const lines = content.split('\n').filter(line => line.trim().length > 0);
  let spaceIndent = 0;
  let tabIndent = 0;
  
  for (const line of lines) {
    if (line.startsWith(' ')) {
      const spaces = line.match(/^ +/)?.[0].length || 0;
      if (spaces > 0) {
        spaceIndent += spaces;
      }
    } else if (line.startsWith('\t')) {
      tabIndent++;
    }
  }
  
  if (spaceIndent > tabIndent) {
    tokens.indent = "spaces";
    // Calculate most common indent size
    const indentSizes = lines
      .map(line => line.match(/^ +/)?.[0].length || 0)
      .filter(size => size > 0);
    const mostCommon = indentSizes.reduce((a, b, i, arr) => 
      arr.filter(v => v === a).length >= arr.filter(v => v === b).length ? a : b, 2
    );
    tokens.indent_size = mostCommon;
  } else {
    tokens.indent = "tabs";
    tokens.indent_size = 1;
  }
  
  // Analyze test framework
  if (content.includes('jest') || content.includes('describe(') || content.includes('it(')) {
    tokens.test_framework = "jest";
  } else if (content.includes('vitest') || content.includes('test(')) {
    tokens.test_framework = "vitest";
  } else if (content.includes('mocha') || content.includes('describe(')) {
    tokens.test_framework = "mocha";
  } else {
    tokens.test_framework = "jest"; // default
  }
  
  // Analyze language
  if (content.includes('interface ') || content.includes('type ') || content.includes(': string')) {
    tokens.language = "typescript";
  } else {
    tokens.language = "javascript";
  }
  
  return tokens;
}

/**
 * Extract style tokens from repository files
 */
async function extractStyleTokens(repoUrl: string, sampleFiles?: string[]): Promise<StyleTokens> {
  // This is a simplified implementation
  // In a real scenario, you would clone the repo and analyze actual files
  
  const defaultTokens: StyleTokens = {
    quotes: "double",
    semicolons: true,
    indent: "spaces",
    indent_size: 2,
    test_framework: "jest",
    directories: ["src", "tests", "lib"],
    aliases: { "@": "src" },
    language: "typescript"
  };
  
  // If sample files are provided, analyze them
  if (sampleFiles && sampleFiles.length > 0) {
    const analyzedTokens: Partial<StyleTokens>[] = [];
    
    for (const fileContent of sampleFiles) {
      const tokens = analyzeCodeStyle(fileContent);
      analyzedTokens.push(tokens);
    }
    
    // Merge analyzed tokens
    const mergedTokens = analyzedTokens.reduce((acc, tokens) => {
      return { ...acc, ...tokens };
    }, defaultTokens);
    
    return mergedTokens as StyleTokens;
  }
  
  return defaultTokens;
}

/**
 * Update user's style profile in the database
 */
async function updateStyleProfile(userId: string, styleTokens: StyleTokens): Promise<boolean> {
  try {
    const { error } = await supabase
      .from('style_profiles')
      .upsert({
        user_id: userId,
        tokens: styleTokens,
        updated_at: new Date().toISOString()
      });
    
    if (error) {
      console.error('Error updating style profile:', error);
      return false;
    }
    
    return true;
  } catch (error) {
    console.error('Exception updating style profile:', error);
    return false;
  }
}

/**
 * Main handler function
 */
serve(async (req) => {
  try {
    // Handle CORS
    if (req.method === 'OPTIONS') {
      return new Response(null, {
        status: 200,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
          'Access-Control-Allow-Methods': 'POST, OPTIONS',
        },
      });
    }
    
    if (req.method !== 'POST') {
      return new Response(
        JSON.stringify({ success: false, error: 'Method not allowed' }),
        { 
          status: 405,
          headers: { 'Content-Type': 'application/json' }
        }
      );
    }
    
    const { repo_url, user_id, sample_files }: RepoAnalysisRequest = await req.json();
    
    if (!repo_url || !user_id) {
      return new Response(
        JSON.stringify({ success: false, error: 'Missing required fields' }),
        { 
          status: 400,
          headers: { 'Content-Type': 'application/json' }
        }
      );
    }
    
    // Extract style tokens from the repository
    const styleTokens = await extractStyleTokens(repo_url, sample_files);
    
    // Update the user's style profile
    const success = await updateStyleProfile(user_id, styleTokens);
    
    if (!success) {
      return new Response(
        JSON.stringify({ success: false, error: 'Failed to update style profile' }),
        { 
          status: 500,
          headers: { 'Content-Type': 'application/json' }
        }
      );
    }
    
    const response: RepoAnalysisResponse = {
      success: true,
      style_tokens: styleTokens
    };
    
    return new Response(
      JSON.stringify(response),
      { 
        status: 200,
        headers: { 
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      }
    );
    
  } catch (error) {
    console.error('Error in analyze_repo function:', error);
    
    const response: RepoAnalysisResponse = {
      success: false,
      error: error.message || 'Internal server error'
    };
    
    return new Response(
      JSON.stringify(response),
      { 
        status: 500,
        headers: { 
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      }
    );
  }
});
