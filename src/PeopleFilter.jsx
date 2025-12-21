import React from 'react';
import { User, ChevronDown } from 'lucide-react';

export default function PeopleFilter({ 
  people = [], 
  selectedPerson, 
  onSelectPerson, 
  showDropdown, 
  setShowDropdown,
  totalCount = 0 
}) {
  if (!Array.isArray(people)) {
    return null;
  }
  
  return (
    <div className="relative mb-4">
      <button
        onClick={() => setShowDropdown(!showDropdown)}
        className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium text-gray-700"
      >
        <User className="w-4 h-4" />
        <span>
          {selectedPerson && selectedPerson.name
            ? `${selectedPerson.name} (${selectedPerson.doc_count || 0})` 
            : `All People (${totalCount || 0})`
          }
        </span>
        <ChevronDown className={`w-4 h-4 transition-transform ${showDropdown ? 'rotate-180' : ''}`} />
      </button>

      {showDropdown && (
        <>
          <div 
            className="fixed inset-0 z-10" 
            onClick={() => setShowDropdown(false)}
          />
          <div className="absolute top-full left-0 mt-1 w-64 bg-white border border-gray-200 rounded-lg shadow-lg z-20 max-h-96 overflow-y-auto">
            <button
              onClick={() => {
                if (onSelectPerson) onSelectPerson(null);
                if (setShowDropdown) setShowDropdown(false);
              }}
              className={`w-full text-left px-4 py-2 hover:bg-gray-50 transition-colors text-sm ${
                !selectedPerson ? 'bg-blue-50 text-blue-700 font-medium' : 'text-gray-700'
              }`}
            >
              All People ({totalCount || 0})
            </button>
            <div className="border-t border-gray-200" />
            {people.map((person, idx) => (
              <button
                key={person?.id || idx}
                onClick={() => {
                  if (onSelectPerson) onSelectPerson(person);
                  if (setShowDropdown) setShowDropdown(false);
                }}
                className={`w-full text-left px-4 py-2 hover:bg-gray-50 transition-colors text-sm ${
                  selectedPerson && selectedPerson.id === person?.id 
                    ? 'bg-blue-50 text-blue-700 font-medium' 
                    : 'text-gray-700'
                }`}
              >
                {person?.name || 'Unknown'} ({person?.doc_count || 0})
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}


