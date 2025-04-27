"""
Educational content for the Escape Room game.
"""

def get_pmbok_content():
    """
    Get educational content for the PMBOK path.
    
    Returns:
        List of dictionaries containing educational content for each PMBOK phase
    """
    return [
        # Initiation Phase
        {
            "title": "Project Initiation",
            "description": "The Initiation phase is where the project is formally authorized and defined.",
            "key_concepts": [
                {
                    "name": "Project Charter",
                    "description": "A document that formally authorizes the project and provides the project manager with the authority to apply organizational resources to project activities."
                },
                {
                    "name": "Stakeholder Identification",
                    "description": "The process of identifying all people or organizations impacted by the project and documenting relevant information regarding their interests, involvement, and impact."
                },
                {
                    "name": "Business Case",
                    "description": "A documented economic feasibility study used to establish the validity of the benefits of a selected component lacking sufficient definition."
                }
            ]
        },
        
        # Planning Phase
        {
            "title": "Project Planning",
            "description": "The Planning phase is where the project scope is defined and the project management plan is developed.",
            "key_concepts": [
                {
                    "name": "Work Breakdown Structure (WBS)",
                    "description": "A hierarchical decomposition of the total scope of work to be carried out by the project team to accomplish the project objectives and create the required deliverables."
                },
                {
                    "name": "Project Schedule",
                    "description": "The planned dates for performing activities and meeting milestones."
                },
                {
                    "name": "Risk Management Plan",
                    "description": "A component of the project management plan that describes how risk management activities will be structured and performed."
                }
            ]
        },
        
        # Execution Phase
        {
            "title": "Project Execution",
            "description": "The Execution phase is where the work defined in the project management plan is completed.",
            "key_concepts": [
                {
                    "name": "Team Management",
                    "description": "The process of tracking team member performance, providing feedback, resolving issues, and managing team changes."
                },
                {
                    "name": "Quality Assurance",
                    "description": "The process of auditing the quality requirements and the results from quality control measurements to ensure appropriate quality standards and operational definitions are used."
                },
                {
                    "name": "Communications Management",
                    "description": "The processes required to ensure timely and appropriate planning, collection, creation, distribution, storage, retrieval, management, control, monitoring, and ultimate disposition of project information."
                }
            ]
        },
        
        # Monitoring and Control Phase
        {
            "title": "Project Monitoring and Control",
            "description": "The Monitoring and Control phase is where project performance is measured and analyzed to identify variances from the project management plan.",
            "key_concepts": [
                {
                    "name": "Earned Value Management",
                    "description": "A methodology that combines scope, schedule, and resource measurements to assess project performance and progress."
                },
                {
                    "name": "Change Control",
                    "description": "The process of reviewing all change requests, approving changes, and managing changes to deliverables, organizational process assets, project documents, and the project management plan."
                },
                {
                    "name": "Performance Reporting",
                    "description": "The process of collecting and distributing performance information, including status reports, progress measurements, and forecasts."
                }
            ]
        },
        
        # Closing Phase
        {
            "title": "Project Closing",
            "description": "The Closing phase is where the project is formally completed and closed.",
            "key_concepts": [
                {
                    "name": "Final Deliverable Acceptance",
                    "description": "The process of obtaining formal acceptance of the completed project deliverables from the customer or sponsor."
                },
                {
                    "name": "Lessons Learned",
                    "description": "The knowledge gained during a project which shows how project events were addressed or should be addressed in the future with the purpose of improving future performance."
                },
                {
                    "name": "Administrative Closure",
                    "description": "The process of finalizing all activities across all project management process groups to formally complete the project or phase."
                }
            ]
        }
    ]

def get_scrum_content():
    """
    Get educational content for the Scrum path.
    
    Returns:
        List of dictionaries containing educational content for each Scrum aspect
    """
    return [
        # Scrum Roles
        {
            "title": "Scrum Roles",
            "description": "Scrum defines three specific roles: Product Owner, Scrum Master, and Development Team.",
            "key_concepts": [
                {
                    "name": "Product Owner",
                    "description": "Responsible for maximizing the value of the product and the work of the Development Team. The Product Owner is the sole person responsible for managing the Product Backlog."
                },
                {
                    "name": "Scrum Master",
                    "description": "Responsible for promoting and supporting Scrum as defined in the Scrum Guide. Scrum Masters do this by helping everyone understand Scrum theory, practices, rules, and values."
                },
                {
                    "name": "Development Team",
                    "description": "Consists of professionals who do the work of delivering a potentially releasable Increment of 'Done' product at the end of each Sprint."
                }
            ]
        },
        
        # Scrum Artifacts
        {
            "title": "Scrum Artifacts",
            "description": "Scrum's artifacts represent work or value to provide transparency and opportunities for inspection and adaptation.",
            "key_concepts": [
                {
                    "name": "Product Backlog",
                    "description": "An ordered list of everything that is known to be needed in the product. It is the single source of requirements for any changes to be made to the product."
                },
                {
                    "name": "Sprint Backlog",
                    "description": "The set of Product Backlog items selected for the Sprint, plus a plan for delivering the product Increment and realizing the Sprint Goal."
                },
                {
                    "name": "Increment",
                    "description": "The sum of all the Product Backlog items completed during a Sprint and the value of the increments of all previous Sprints."
                }
            ]
        },
        
        # Scrum Events
        {
            "title": "Scrum Events",
            "description": "Prescribed events are used in Scrum to create regularity and to minimize the need for meetings not defined in Scrum.",
            "key_concepts": [
                {
                    "name": "Sprint",
                    "description": "A time-box of one month or less during which a 'Done', useable, and potentially releasable product Increment is created."
                },
                {
                    "name": "Sprint Planning",
                    "description": "The event where the work to be performed in the Sprint is planned. This plan is created by the collaborative work of the entire Scrum Team."
                },
                {
                    "name": "Daily Scrum",
                    "description": "A 15-minute time-boxed event for the Development Team to synchronize activities and create a plan for the next 24 hours."
                },
                {
                    "name": "Sprint Review",
                    "description": "An event held at the end of the Sprint to inspect the Increment and adapt the Product Backlog if needed."
                },
                {
                    "name": "Sprint Retrospective",
                    "description": "An opportunity for the Scrum Team to inspect itself and create a plan for improvements to be enacted during the next Sprint."
                }
            ]
        }
    ]
