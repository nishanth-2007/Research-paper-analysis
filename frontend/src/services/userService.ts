import { supabase, isSupabaseConfigured } from './supabase';

export interface UserMapping {
  username: string;
  email: string;
  userId?: string;
  createdAt?: string;
}

const REGISTRY_STORAGE_KEY = 'journal_readiness_user_registry';

/**
 * Pre-seeded known user mappings and initial registry loader
 */
function getLocalRegistry(): UserMapping[] {
  try {
    const raw = localStorage.getItem(REGISTRY_STORAGE_KEY);
    const registry: UserMapping[] = raw ? JSON.parse(raw) : [];

    // Also include any currently logged-in user session if present
    const savedUser = localStorage.getItem('journal_readiness_user');
    if (savedUser) {
      const parsed = JSON.parse(savedUser);
      if (parsed?.username && parsed?.email) {
        if (!registry.some((u) => u.username.toLowerCase() === parsed.username.toLowerCase())) {
          registry.push({
            username: parsed.username,
            email: parsed.email,
          });
        }
      }
    }

    // Include primary developer/owner mapping as seed
    if (!registry.some((u) => u.username.toLowerCase() === 'nishanthg')) {
      registry.push({
        username: 'Nishanthg',
        email: 'godasunishanth04@gmail.com',
      });
    }

    return registry;
  } catch (err) {
    console.warn('Failed to parse user registry from localStorage:', err);
    return [
      {
        username: 'Nishanthg',
        email: 'godasunishanth04@gmail.com',
      },
    ];
  }
}

function saveLocalRegistry(registry: UserMapping[]): void {
  try {
    localStorage.setItem(REGISTRY_STORAGE_KEY, JSON.stringify(registry));
  } catch (err) {
    console.warn('Failed to save user registry to localStorage:', err);
  }
}

export const UserService = {
  /**
   * Validates whether a username is already taken across Supabase database and local registry.
   */
  async checkUsernameAvailable(username: string): Promise<{ available: boolean; reason?: string }> {
    const cleanUsername = username.trim();
    if (!cleanUsername) {
      return { available: false, reason: 'Please enter a username.' };
    }

    if (cleanUsername.length < 3) {
      return { available: false, reason: 'Username must be at least 3 characters long.' };
    }

    if (!/^[a-zA-Z0-9_.-]+$/.test(cleanUsername)) {
      return {
        available: false,
        reason: 'Username can only contain letters, numbers, underscores (_), hyphens (-), and dots (.).',
      };
    }

    // 1. Check in Supabase 'profiles' table (if configured and table exists)
    if (isSupabaseConfigured && supabase) {
      try {
        const { data, error } = await supabase
          .from('profiles')
          .select('id, username')
          .ilike('username', cleanUsername)
          .limit(1);

        if (!error && data && data.length > 0) {
          return {
            available: false,
            reason: `The username "${cleanUsername}" is already taken. Please choose another username.`,
          };
        }
      } catch (err) {
        // Table may not exist yet in Supabase schema cache; proceed to local registry check
      }
    }

    // 2. Check in Local / Cached Registry (case-insensitive)
    const registry = getLocalRegistry();
    const existing = registry.find(
      (u) => u.username.toLowerCase() === cleanUsername.toLowerCase()
    );

    if (existing) {
      return {
        available: false,
        reason: `The username "${cleanUsername}" is already taken. Please choose another username.`,
      };
    }

    return { available: true };
  },

  /**
   * Resolves an identifier (either email or username) into a valid email address for Supabase authentication.
   */
  async resolveEmailFromIdentifier(identifier: string): Promise<string | null> {
    const cleanId = identifier.trim();
    if (!cleanId) return null;

    // If identifier is already an email format, return directly
    if (cleanId.includes('@')) {
      return cleanId;
    }

    // 1. Look up in Supabase 'profiles' table if available
    if (isSupabaseConfigured && supabase) {
      try {
        const { data, error } = await supabase
          .from('profiles')
          .select('email, username')
          .ilike('username', cleanId)
          .limit(1);

        if (!error && data && data.length > 0 && data[0].email) {
          // Cache in local registry
          this.registerUserMapping(data[0].username, data[0].email);
          return data[0].email;
        }
      } catch (err) {
        // Graceful fallback to local registry
      }
    }

    // 2. Look up in Local / Cached Registry (case-insensitive)
    const registry = getLocalRegistry();
    const match = registry.find(
      (u) => u.username.toLowerCase() === cleanId.toLowerCase()
    );

    if (match) {
      return match.email;
    }

    return null;
  },

  /**
   * Registers a username <-> email mapping to both Supabase profiles and local persistent storage.
   */
  async registerUserMapping(username: string, email: string, userId?: string): Promise<void> {
    const cleanUser = username.trim();
    const cleanEmail = email.trim();

    // 1. Update local registry
    const registry = getLocalRegistry();
    const existingIndex = registry.findIndex(
      (u) => u.username.toLowerCase() === cleanUser.toLowerCase()
    );

    if (existingIndex >= 0) {
      registry[existingIndex] = {
        ...registry[existingIndex],
        email: cleanEmail,
        userId: userId || registry[existingIndex].userId,
      };
    } else {
      registry.push({
        username: cleanUser,
        email: cleanEmail,
        userId,
        createdAt: new Date().toISOString(),
      });
    }
    saveLocalRegistry(registry);

    // 2. Attempt sync to Supabase 'profiles' table if accessible
    if (isSupabaseConfigured && supabase) {
      try {
        await supabase.from('profiles').upsert(
          [
            {
              id: userId || undefined,
              username: cleanUser,
              email: cleanEmail,
            },
          ],
          { onConflict: 'username' }
        );
      } catch (err) {
        // Table might not exist yet; local registry remains active
      }
    }
  },

  /**
   * SQL Schema setup helper for Supabase users who want global server-side table enforcement.
   */
  getSupabaseSetupSql(): string {
    return `
-- Run this in your Supabase SQL Editor to enforce global username uniqueness & resolution:
create table if not exists public.profiles (
  id uuid references auth.users on delete cascade primary key,
  username text unique not null,
  email text not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Enable Row Level Security
alter table public.profiles enable row level security;

-- Allow public read so the login screen can lookup email by username
create policy "Allow public read for username lookup" on public.profiles
  for select using (true);

-- Allow authenticated users to insert/update their own profile
create policy "Allow insert profile" on public.profiles
  for insert with check (true);

create policy "Allow update own profile" on public.profiles
  for update using (auth.uid() = id);
`.trim();
  },
};
