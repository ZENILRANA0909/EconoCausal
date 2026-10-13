const API = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1';
export async function getJson<T>(path:string):Promise<T>{
  const res=await fetch(`${API}${path}`);
  if(!res.ok) throw new Error(`API ${res.status}: ${await res.text()}`);
  return res.json() as Promise<T>;
}
export type Summary={rows:number;columns:number;valid:boolean;synthetic:boolean;purchase_rate:number;mean_income:number;mean_aov:number;treatment_rate:number;segment_counts:Record<string,number>};
export type Customer={customer_id:string;age:number;income:number;previous_purchases:number;website_visits:number;customer_segment:string;discount_received:number;purchase:number;historical_aov:number;contribution_margin:number};
