import React, { useState, useEffect } from 'react';
import { DomainExpert } from './DomainExpertsManager';
import { FaRunning, FaMedal, FaAppleAlt, FaMedkit } from 'react-icons/fa';

interface DomainExpertSelectorProps {
  experts: DomainExpert[];
  selectedExpertId: string | null;
  onSelectExpert: (expertId: string | null) => void;
}

const DomainExpertSelector: React.FC<DomainExpertSelectorProps> = ({
  experts,
  selectedExpertId,
  onSelectExpert,
}) => {
  const [isOpen, setIsOpen] = useState(false);

  const getIconComponent = (iconName: string) => {
    switch (iconName) {
      case 'running':
        return <FaRunning />;
      case 'medal':
        return <FaMedal />;
      case 'nutrition':
        return <FaAppleAlt />;
      case 'medical':
        return <FaMedkit />;
      default:
        return null;
    }
  };

  const selectedExpert = experts.find(expert => expert.id === selectedExpertId) || experts[0];

  return (
    <div className="relative">
      <div className="flex flex-col space-y-2">
        <label className="text-sm font-medium text-dark dark:text-light">
          Domain Expert
        </label>
        <div
          className="flex items-center p-2 border border-gray-300 dark:border-gray-700 rounded-md bg-light dark:bg-dark cursor-pointer"
          onClick={() => setIsOpen(!isOpen)}
        >
          <div className="flex items-center space-x-2">
            <span className="text-primary dark:text-primaryDark">
              {selectedExpert && getIconComponent(selectedExpert.icon)}
            </span>
            <span className="text-sm">
              {selectedExpert ? selectedExpert.name : 'Select Domain Expert'}
            </span>
            {selectedExpert?.isExperimental && (
              <span className="text-xs px-2 py-1 bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 rounded-md">
                Experimental
              </span>
            )}
          </div>
          <span className="ml-auto">{isOpen ? '▲' : '▼'}</span>
        </div>
      </div>

      {isOpen && (
        <div className="absolute z-10 mt-1 w-full bg-light dark:bg-dark border border-gray-300 dark:border-gray-700 rounded-md shadow-lg">
          <ul className="py-1">
            <li 
              className={`px-3 py-2 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800 ${!selectedExpertId ? 'bg-gray-100 dark:bg-gray-800' : ''}`}
              onClick={() => {
                onSelectExpert(null);
                setIsOpen(false);
              }}
            >
              <div className="flex items-center">
                <span className="ml-2">Auto-select best expert</span>
              </div>
            </li>
            
            {experts.map(expert => (
              <li
                key={expert.id}
                className={`px-3 py-2 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800 ${expert.id === selectedExpertId ? 'bg-gray-100 dark:bg-gray-800' : ''} ${!expert.isAvailable ? 'opacity-50' : ''}`}
                onClick={() => {
                  if (expert.isAvailable) {
                    onSelectExpert(expert.id);
                    setIsOpen(false);
                  }
                }}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="text-primary dark:text-primaryDark">
                      {getIconComponent(expert.icon)}
                    </span>
                    <span>{expert.name}</span>
                  </div>
                  {expert.isExperimental && (
                    <span className="text-xs px-2 py-1 bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 rounded-md">
                      Experimental
                    </span>
                  )}
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400 ml-6">
                  {expert.description}
                </p>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default DomainExpertSelector;
