import React, { useState } from 'react';
import { TestimonialCard } from './ui/testimonial-cards';

export function RecentInvestigationsStacked({ cases, onCaseClick }: { cases: any[], onCaseClick: (c: any) => void }) {
    const [items, setItems] = useState(
        cases.slice(0, 3).map((c: any, i: number) => ({
            ...c,
            position: i === 0 ? 'front' : i === 1 ? 'middle' : 'back',
        }))
    );

    const handleShuffle = () => {
        setItems((prevItems: any[]) => {
            const newItems = [...prevItems];
            const frontItem = newItems.shift();
            if (frontItem) {
                frontItem.position = 'back';
                newItems.push(frontItem);
            }
            // Update positions
            newItems.forEach((item: any, index: number) => {
                item.position = index === 0 ? 'front' : index === 1 ? 'middle' : 'back';
            });
            return newItems;
        });
    };

    if (cases.length === 0) {
        return <div className="text-cream-dim text-sm py-4">No recent investigations.</div>;
    }

    return (
        <div className="relative h-[500px] w-full flex items-center justify-center p-8 bg-black/20 rounded-xl border border-servos-border">
            {items.map((item: any) => (
                <TestimonialCard
                    key={item.id}
                    id={item.id}
                    author={item.investigator}
                    testimonial={`Case ${item.id.slice(0, 8)} - ${item.mode.toUpperCase()}`}
                    position={item.position}
                    handleShuffle={handleShuffle}
                />
            ))}
            <div className="absolute bottom-4 text-xs text-cream-dim animate-pulse">
                Drag the front card to shuffle
            </div>
        </div>
    );
}
