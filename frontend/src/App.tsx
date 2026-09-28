import React, { useState, useEffect } from 'react';
import { AppShell } from './components/AppShell';
import { OverviewView } from './views/OverviewView';
import { MaintenanceView } from './views/MaintenanceView';
import { PlanningView } from './views/PlanningView';
import { ChangeReviewView } from './views/ChangeReviewView';
import { EvaluationView } from './views/EvaluationView';
import { ApprovalView } from './views/ApprovalView';
import { RulesView } from './views/RulesView';
import { DataView } from './views/DataView';
import { AuditView } from './views/AuditView';
import { ComponentGalleryView } from './views/ComponentGalleryView';
import { LandingPageView } from './views/LandingPageView';
import { FieldReporterView } from './views/FieldReporterView';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>(() => {
    if (window.location.pathname === '/field-reporter') {
      return 'field-reporter';
    }
    const params = new URLSearchParams(window.location.search);
    return params.get('view') || 'landing';
  });

  useEffect(() => {
    const handlePopState = () => {
      if (window.location.pathname === '/field-reporter') {
        setActiveTab('field-reporter');
        return;
      }
      const params = new URLSearchParams(window.location.search);
      setActiveTab(params.get('view') || 'landing');
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const handleTabChange = (tab: string) => {
    setActiveTab(tab);
    const url = new URL(window.location.href);
    if (tab === 'field-reporter') {
      url.pathname = '/field-reporter';
      url.searchParams.delete('view');
    } else {
      url.pathname = '/';
      url.searchParams.set('view', tab);
    }
    window.history.pushState({}, '', url.toString());
  };

  // Landing page is a full-screen experience outside the AppShell
  if (activeTab === 'landing') {
    return (
      <LandingPageView
        onEnterWorkbench={(view?: string) => handleTabChange(view || 'overview')}
      />
    );
  }

  const renderContent = () => {
    switch (activeTab) {
      case 'overview':
        return (
          <OverviewView
            onNavigateToPlanning={() => handleTabChange('planning')}
            onNavigateToMaintenance={() => handleTabChange('maintenance')}
          />
        );
      case 'maintenance':
        return <MaintenanceView />;
      case 'planning':
        return <PlanningView />;
      case 'change-review':
        return <ChangeReviewView />;
      case 'field-reporter':
        return <FieldReporterView onNavigateToCockpit={() => handleTabChange('change-review')} />;
      case 'evaluation':
        return <EvaluationView />;
      case 'approval':
        return <ApprovalView />;
      case 'rules':
        return <RulesView />;
      case 'data':
        return <DataView />;
      case 'audit':
        return <AuditView />;
      case 'gallery':
        return <ComponentGalleryView />;
      default:
        return <OverviewView />;
    }
  };

  return (
    <AppShell activeTab={activeTab} onTabChange={handleTabChange}>
      {renderContent()}
    </AppShell>
  );
};

export default App;
