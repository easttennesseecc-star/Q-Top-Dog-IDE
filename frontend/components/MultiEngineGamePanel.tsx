/**
 * Multi-Engine Game Development Panel
 * Provides UI for switching between engines and managing game engine projects
 */

import React, { useState, useEffect } from 'react';
import styled from 'styled-components';

// ==================== STYLED COMPONENTS ====================

const PanelContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #1e1e1e;
  color: #d4d4d4;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: #252526;
  border-bottom: 1px solid #3e3e42;
`;

const Title = styled.h2`
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const EngineSelector = styled.div`
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  border-bottom: 1px solid #3e3e42;
  background: #252526;
`;

const EngineButton = styled.button`
  flex: 1;
  padding: 8px 12px;
  background: ${props => props.active ? '#0e639c' : '#3e3e42'};
  color: ${props => props.active ? '#fff' : '#d4d4d4'};
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.2s ease;

  &:hover {
    background: ${props => props.active ? '#1177bb' : '#4e4e52'};
  }
`;

const ContentArea = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 12px 16px;
`;

const Section = styled.div`
  margin-bottom: 16px;
`;

const SectionTitle = styled.h3`
  margin: 0 0 8px 0;
  font-size: 12px;
  font-weight: 600;
  color: #858585;
  text-transform: uppercase;
`;

const ProjectList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const ProjectItem = styled.div`
  padding: 8px 12px;
  background: #2d2d30;
  border: 1px solid #3e3e42;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: #3e3e42;
    border-color: #0e639c;
  }

  ${props => props.active && `
    background: #1e3a5f;
    border-color: #0e639c;
  `}
`;

const ProjectName = styled.div`
  font-size: 12px;
  font-weight: 500;
  color: #d4d4d4;
`;

const ProjectPath = styled.div`
  font-size: 11px;
  color: #858585;
  margin-top: 4px;
`;

const ContainerStatus = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
`;

const StatusIndicator = styled.div`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: ${props => {
    switch (props.status) {
      case 'running': return '#89d185';
      case 'stopped': return '#858585';
      case 'error': return '#f48771';
      default: return '#858585';
    }
  }};
`;

const StatusText = styled.div`
  font-size: 10px;
  color: #858585;
  text-transform: uppercase;
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 4px;
  margin-top: 8px;
`;

const ActionButton = styled.button`
  flex: 1;
  padding: 6px 8px;
  background: #0e639c;
  color: #fff;
  border: none;
  border-radius: 3px;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: #1177bb;
  }

  ${props => props.secondary && `
    background: #3e3e42;
    color: #d4d4d4;

    &:hover {
      background: #4e4e52;
    }
  `}

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const PreviewContainer = styled.div`
  width: 100%;
  height: 300px;
  background: #000;
  border: 1px solid #3e3e42;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: #858585;
  overflow: hidden;
`;

const PreviewIframe = styled.iframe`
  width: 100%;
  height: 100%;
  border: none;
`;

// ==================== COMPONENT ====================

const MultiEngineGamePanel = () => {
  const [activeEngine, setActiveEngine] = useState('construct3');
  const [projects, setProjects] = useState([]);
  const [activeProject, setActiveProject] = useState(null);
  const [containers, setContainers] = useState([]);
  const [loading, setLoading] = useState(false);

  const engines = [
    { id: 'construct3', name: 'Construct 3', icon: '🎮' },
    { id: 'godot', name: 'Godot', icon: '🔧' },
    { id: 'unity', name: 'Unity', icon: '⚙️' },
    { id: 'unreal', name: 'Unreal', icon: '🚀' },
  ];

  // Fetch projects on mount
  useEffect(() => {
    loadProjects();
    loadContainers();

    // Refresh containers every 5 seconds
    const interval = setInterval(loadContainers, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadProjects = async () => {
    try {
      const response = await fetch('/api/v1/game-engine/projects');
      const data = await response.json();
      if (data.success) {
        setProjects(data.projects);
        if (data.projects.length > 0 && !activeProject) {
          setActiveProject(data.projects[0].project_id);
        }
      }
    } catch (error) {
      console.error('Error loading projects:', error);
    }
  };

  const loadContainers = async () => {
    try {
      const response = await fetch('/api/v1/game-engine/containers');
      const data = await response.json();
      if (data.success) {
        setContainers(data.containers);
      }
    } catch (error) {
      console.error('Error loading containers:', error);
    }
  };

  const handleSwitchEngine = (engineId) => {
    setActiveEngine(engineId);
    // Filter projects for this engine
    const engineProjects = projects.filter(p => p.engine === engineId);
    if (engineProjects.length > 0) {
      setActiveProject(engineProjects[0].project_id);
    }
  };

  const handleSwitchProject = async (projectId) => {
    try {
      setLoading(true);
      const response = await fetch(
        `/api/v1/game-engine/projects/${projectId}/switch`,
        { method: 'POST' }
      );
      const data = await response.json();
      if (data.success) {
        setActiveProject(projectId);
      }
    } catch (error) {
      console.error('Error switching project:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStartContainer = async (projectId) => {
    try {
      setLoading(true);
      const project = projects.find(p => p.project_id === projectId);
      
      const response = await fetch('/api/v1/game-engine/containers/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: projectId,
          engine: project.engine,
          project_path: project.path,
        }),
      });

      const data = await response.json();
      if (data.success) {
        loadContainers();
      }
    } catch (error) {
      console.error('Error starting container:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStopContainer = async (projectId) => {
    try {
      setLoading(true);
      const response = await fetch(
        `/api/v1/game-engine/containers/${projectId}`,
        { method: 'DELETE' }
      );

      const data = await response.json();
      if (data.success) {
        loadContainers();
      }
    } catch (error) {
      console.error('Error stopping container:', error);
    } finally {
      setLoading(false);
    }
  };

  const getEngineProjects = () => {
    return projects.filter(p => p.engine === activeEngine);
  };

  const getContainerForProject = (projectId) => {
    return containers.find(c => c.project_id === projectId);
  };

  const activeEngineData = engines.find(e => e.id === activeEngine);
  const engineProjects = getEngineProjects();

  return (
    <PanelContainer>
      <Header>
        <Title>🎮 Game Engines</Title>
      </Header>

      <EngineSelector>
        {engines.map(engine => (
          <EngineButton
            key={engine.id}
            active={activeEngine === engine.id}
            onClick={() => handleSwitchEngine(engine.id)}
            title={engine.name}
          >
            {engine.icon} {engine.name}
          </EngineButton>
        ))}
      </EngineSelector>

      <ContentArea>
        {/* Projects Section */}
        <Section>
          <SectionTitle>{activeEngineData.name} Projects</SectionTitle>
          <ProjectList>
            {engineProjects.length > 0 ? (
              engineProjects.map(project => {
                const container = getContainerForProject(project.project_id);
                const isActive = project.project_id === activeProject;

                return (
                  <ProjectItem
                    key={project.project_id}
                    active={isActive}
                    onClick={() => handleSwitchProject(project.project_id)}
                  >
                    <ProjectName>{project.project_id}</ProjectName>
                    <ProjectPath>{project.path}</ProjectPath>

                    {container && (
                      <ContainerStatus>
                        <StatusIndicator status={container.status} />
                        <StatusText>{container.status}</StatusText>
                      </ContainerStatus>
                    )}

                    {activeEngine !== 'construct3' && activeEngine !== 'unity' && (
                      <ActionButtons>
                        {!container || container.status === 'stopped' ? (
                          <ActionButton
                            onClick={(e) => {
                              e.stopPropagation();
                              handleStartContainer(project.project_id);
                            }}
                            disabled={loading}
                          >
                            Start Container
                          </ActionButton>
                        ) : (
                          <ActionButton
                            secondary
                            onClick={(e) => {
                              e.stopPropagation();
                              handleStopContainer(project.project_id);
                            }}
                            disabled={loading}
                          >
                            Stop Container
                          </ActionButton>
                        )}
                      </ActionButtons>
                    )}
                  </ProjectItem>
                );
              })
            ) : (
              <ProjectPath style={{ color: '#858585' }}>
                No {activeEngineData.name} projects found
              </ProjectPath>
            )}
          </ProjectList>
        </Section>

        {/* Game Preview Section */}
        {activeProject && (
          <Section>
            <SectionTitle>Game Preview</SectionTitle>
            <PreviewContainer>
              {getContainerForProject(activeProject)?.status === 'running' ? (
                <PreviewIframe
                  src={`http://localhost:${getContainerForProject(activeProject).port_mapping.preview}`}
                  title="Game Preview"
                />
              ) : (
                <div>Game preview unavailable. Start container to preview.</div>
              )}
            </PreviewContainer>
          </Section>
        )}

        {/* Container Status Section */}
        {containers.length > 0 && (
          <Section>
            <SectionTitle>Active Containers</SectionTitle>
            <ProjectList>
              {containers.map(container => (
                <ProjectItem key={container.project_id}>
                  <ProjectName>{container.engine.toUpperCase()}</ProjectName>
                  <ContainerStatus>
                    <StatusIndicator status={container.status} />
                    <StatusText>{container.status}</StatusText>
                  </ContainerStatus>
                  <ProjectPath style={{ fontSize: '11px' }}>
                    Debug: :{container.port_mapping.debug} |{' '}
                    Preview: :{container.port_mapping.preview}
                  </ProjectPath>
                </ProjectItem>
              ))}
            </ProjectList>
          </Section>
        )}
      </ContentArea>
    </PanelContainer>
  );
};

export default MultiEngineGamePanel;
