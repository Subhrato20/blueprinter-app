import { createClient } from '@supabase/supabase-js'
import type { Database } from './database.types'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || import.meta.env.NEXT_PUBLIC_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || import.meta.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

console.log('Supabase URL:', supabaseUrl ? 'Set' : 'Missing')
console.log('Supabase Key:', supabaseAnonKey ? 'Set' : 'Missing')

// Create mock client for when Supabase is not configured
const mockClient = {
  auth: {
    signInWithOAuth: () => Promise.resolve({ error: new Error('Supabase not configured') }),
    signOut: () => Promise.resolve({ error: null }),
    getUser: () => Promise.resolve({ data: { user: null }, error: null }),
    onAuthStateChange: () => ({ data: { subscription: { unsubscribe: () => {} } } })
  }
}

// Export the appropriate client
export const supabase = (!supabaseUrl || !supabaseAnonKey) 
  ? mockClient as any
  : createClient<Database>(supabaseUrl, supabaseAnonKey, {
      auth: {
        autoRefreshToken: true,
        persistSession: true,
        detectSessionInUrl: true
      },
      realtime: {
        params: {
          eventsPerSecond: 10
        }
      }
    })

// Auth helpers
export const signInWithGitHub = async () => {
  const { data, error } = await supabase.auth.signInWithOAuth({
    provider: 'github',
    options: {
      redirectTo: `${window.location.origin}/auth/callback`
    }
  })
  return { data, error }
}

export const signOut = async () => {
  const { error } = await supabase.auth.signOut()
  return { error }
}

export const getCurrentUser = async () => {
  const { data: { user }, error } = await supabase.auth.getUser()
  return { user, error }
}

// Database helpers
export const getProjects = async (userId: string) => {
  const { data, error } = await supabase
    .from('projects')
    .select('*')
    .eq('owner', userId)
    .order('created_at', { ascending: false })
  
  return { data, error }
}

export const createProject = async (name: string, description?: string) => {
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) throw new Error('Not authenticated')

  const { data, error } = await supabase
    .from('projects')
    .insert({
      name,
      description,
      owner: user.id
    })
    .select()
    .single()

  return { data, error }
}

export const getPlans = async (projectId: string) => {
  const { data, error } = await supabase
    .from('plans')
    .select('*')
    .eq('project_id', projectId)
    .order('created_at', { ascending: false })
  
  return { data, error }
}

export const getPlan = async (planId: string) => {
  const { data, error } = await supabase
    .from('plans')
    .select('*')
    .eq('id', planId)
    .single()
  
  return { data, error }
}

export const getStyleProfile = async (userId: string) => {
  const { data, error } = await supabase
    .from('style_profiles')
    .select('*')
    .eq('user_id', userId)
    .single()
  
  return { data, error }
}

export const updateStyleProfile = async (userId: string, tokens: any) => {
  const { data, error } = await supabase
    .from('style_profiles')
    .upsert({
      user_id: userId,
      tokens,
      updated_at: new Date().toISOString()
    })
    .select()
    .single()

  return { data, error }
}

// Realtime subscriptions
export const subscribeToPlans = (projectId: string, callback: (payload: any) => void) => {
  return supabase
    .channel('plans')
    .on(
      'postgres_changes',
      {
        event: '*',
        schema: 'public',
        table: 'plans',
        filter: `project_id=eq.${projectId}`
      },
      callback
    )
    .subscribe()
}

export const subscribeToPlanMessages = (planId: string, callback: (payload: any) => void) => {
  return supabase
    .channel('plan_messages')
    .on(
      'postgres_changes',
      {
        event: '*',
        schema: 'public',
        table: 'plan_messages',
        filter: `plan_id=eq.${planId}`
      },
      callback
    )
    .subscribe()
}
