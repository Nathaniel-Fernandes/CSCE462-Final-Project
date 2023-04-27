
export interface User {
    id?: number,
    first_name: string,
    last_name: string,
    dob: string, // date 
    uuid: string,
    start_date: string, // date
    role: string, // text
    department: string,
    salary: string,
    phone_number: string
}

export interface Event {
    id: bigint;
    inserted_at: string; // timestamp with time zone
    updated_at: string; // timestamp with time zone
    event: string; // public.event
    cabinet_id: string; // not nullable
    scan_result?: Record<string, unknown> | null; // jsonb
    user?: string | null;
}

export interface ItemType {
    id: bigint;
    created_at?: string | null; // timestamp with time zone
    name: string; // not nullable
}

export interface Item {
    id: bigint;
    name: string; // not nullable
    expiration?: string | null; // date
    uuid?: string | null;
    type?: string | null; // foreign key reference to ItemTypes.name
}

export interface Permission {
    id: bigint;
    created_at?: string | null; // timestamp with time zone
    personnel_uuid: string; // not nullable
    cabinet_id: string; // not nullable
}