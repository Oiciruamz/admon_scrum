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
            ],
            "quiz_questions": [
                {
                    "question": "What document formally authorizes a project?",
                    "options": ["Project Charter", "Business Case", "Scope Statement", "Project Plan"],
                    "correct_answer": "Project Charter"
                },
                {
                    "question": "Who approves the Project Charter?",
                    "options": ["Project Manager", "Sponsor", "Team Members", "Stakeholders"],
                    "correct_answer": "Sponsor"
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
            ],
            "quiz_questions": [
                {
                    "question": "What is the purpose of a Work Breakdown Structure (WBS)?",
                    "options": [
                        "To assign resources to tasks",
                        "To decompose project deliverables into smaller components",
                        "To schedule project activities",
                        "To identify project risks"
                    ],
                    "correct_answer": "To decompose project deliverables into smaller components"
                },
                {
                    "question": "Which of the following is NOT typically included in project planning?",
                    "options": [
                        "Schedule development",
                        "Budget estimation",
                        "Project execution",
                        "Risk identification"
                    ],
                    "correct_answer": "Project execution"
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
            ],
            "quiz_questions": [
                {
                    "question": "What is the main focus of the Execution phase?",
                    "options": [
                        "Planning project activities",
                        "Completing the work defined in the project plan",
                        "Monitoring project progress",
                        "Closing the project"
                    ],
                    "correct_answer": "Completing the work defined in the project plan"
                },
                {
                    "question": "Which of the following is a key responsibility during project execution?",
                    "options": [
                        "Creating the project charter",
                        "Developing the WBS",
                        "Managing the project team",
                        "Closing procurement contracts"
                    ],
                    "correct_answer": "Managing the project team"
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
            ],
            "quiz_questions": [
                {
                    "question": "What is the purpose of Earned Value Management?",
                    "options": [
                        "To manage project resources",
                        "To measure project performance and progress",
                        "To identify project stakeholders",
                        "To develop the project schedule"
                    ],
                    "correct_answer": "To measure project performance and progress"
                },
                {
                    "question": "Which of the following is NOT a key process in the Monitoring and Control phase?",
                    "options": [
                        "Controlling changes",
                        "Monitoring risks",
                        "Creating the project charter",
                        "Verifying scope"
                    ],
                    "correct_answer": "Creating the project charter"
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
            ],
            "quiz_questions": [
                {
                    "question": "What is the main purpose of the Closing phase?",
                    "options": [
                        "To plan project activities",
                        "To execute project work",
                        "To monitor project progress",
                        "To formally complete the project"
                    ],
                    "correct_answer": "To formally complete the project"
                },
                {
                    "question": "Which document captures knowledge gained during a project for future reference?",
                    "options": [
                        "Project Charter",
                        "Lessons Learned",
                        "Work Breakdown Structure",
                        "Risk Register"
                    ],
                    "correct_answer": "Lessons Learned"
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
            ],
            "quiz_questions": [
                {
                    "question": "Who is responsible for managing the Product Backlog?",
                    "options": ["Scrum Master", "Product Owner", "Development Team", "Project Manager"],
                    "correct_answer": "Product Owner"
                },
                {
                    "question": "What is the primary responsibility of the Scrum Master?",
                    "options": [
                        "Managing the team",
                        "Promoting and supporting Scrum",
                        "Developing the product",
                        "Setting project deadlines"
                    ],
                    "correct_answer": "Promoting and supporting Scrum"
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
            ],
            "quiz_questions": [
                {
                    "question": "What is the Product Backlog?",
                    "options": [
                        "A list of tasks for the current Sprint",
                        "An ordered list of everything needed in the product",
                        "A list of completed features",
                        "A report of project progress"
                    ],
                    "correct_answer": "An ordered list of everything needed in the product"
                },
                {
                    "question": "What is included in the Sprint Backlog?",
                    "options": [
                        "All items in the Product Backlog",
                        "Selected Product Backlog items and a plan for delivering them",
                        "A list of all project requirements",
                        "Completed work from previous Sprints"
                    ],
                    "correct_answer": "Selected Product Backlog items and a plan for delivering them"
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
            ],
            "quiz_questions": [
                {
                    "question": "What is the maximum duration of a Sprint?",
                    "options": ["One week", "Two weeks", "One month", "Three months"],
                    "correct_answer": "One month"
                },
                {
                    "question": "What is the purpose of the Daily Scrum?",
                    "options": [
                        "To report progress to the Product Owner",
                        "To synchronize activities and plan for the next 24 hours",
                        "To update the Sprint Backlog",
                        "To review completed work"
                    ],
                    "correct_answer": "To synchronize activities and plan for the next 24 hours"
                }
            ]
        },
        
        # Scrum Values
        {
            "title": "Scrum Values",
            "description": "When the values of commitment, courage, focus, openness, and respect are embodied and lived by the Scrum Team, the Scrum pillars of transparency, inspection, and adaptation come to life.",
            "key_concepts": [
                {
                    "name": "Commitment",
                    "description": "The Scrum Team commits to achieving its goals and to supporting each other."
                },
                {
                    "name": "Courage",
                    "description": "The Scrum Team members have courage to do the right thing and work on tough problems."
                },
                {
                    "name": "Focus",
                    "description": "Everyone focuses on the work of the Sprint and the goals of the Scrum Team."
                },
                {
                    "name": "Openness",
                    "description": "The Scrum Team and its stakeholders agree to be open about all the work and the challenges with performing the work."
                },
                {
                    "name": "Respect",
                    "description": "Scrum Team members respect each other to be capable, independent people."
                }
            ],
            "quiz_questions": [
                {
                    "question": "Which of the following is NOT one of the five Scrum values?",
                    "options": ["Commitment", "Courage", "Efficiency", "Respect"],
                    "correct_answer": "Efficiency"
                },
                {
                    "question": "How do Scrum values relate to Scrum pillars?",
                    "options": [
                        "They are unrelated concepts",
                        "When values are embodied, pillars come to life",
                        "Pillars replace values in modern Scrum",
                        "Values are more important than pillars"
                    ],
                    "correct_answer": "When values are embodied, pillars come to life"
                }
            ]
        }
    ]
