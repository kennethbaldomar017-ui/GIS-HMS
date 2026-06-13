"use client";

import dynamic from "next/dynamic";

export const DynamicMap = dynamic(() => import("./MapView").then((m) => m.MapView), { ssr: false, loading: () => <div className="grid h-[calc(100vh-8rem)] place-items-center">Loading map...</div> });
